#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
FreeZap Agent v1.0.0 — Freebox v6 Revolution bridge

Local HTTP bridge between FreeZap (browser) and the authenticated
Freebox OS API. Reads real-time player status (powered, channel,
volume) and exposes it on http://localhost:8766/ with CORS so
FreeZap JavaScript can poll it.

Stack:   Python 3.6+ stdlib only — no pip install needed.
License: MIT (same as FreeZap)
═══════════════════════════════════════════════════════════════════
"""

import http.server
import hashlib
import hmac
import json
import os
import socketserver
import sys
import threading
import time
import urllib.error
import urllib.request

# ─── Config ───────────────────────────────────────────────────────
APP_ID = "freezap"
APP_NAME = "FreeZap"
APP_VERSION = "1.1.0"
DEVICE_NAME = "FreeZap Agent"
FREEBOX_BASE = "http://mafreebox.freebox.fr"
TOKEN_FILE = os.path.expanduser("~/.freezap/token.json")
POLL_INTERVAL = 2.0
SESSION_RENEW_SECONDS = 25 * 60  # 25 minutes
LISTEN_PORT = int(os.environ.get("FREEZAP_AGENT_PORT", "8766"))


# ─── Freebox Client ───────────────────────────────────────────────
class FreeboxClient:
    """
    Handles pairing, session auth, polling the player status endpoint,
    and caching the result in memory for the HTTP server to serve.
    """

    def __init__(self):
        self.app_token = None
        self.session_token = None
        self.session_expires_at = 0
        self.player_id = None
        self.last_status = None
        self.lock = threading.Lock()
        self._load_token()

    # ── token persistence ─────────────────────────────────────────
    def _load_token(self):
        try:
            with open(TOKEN_FILE) as f:
                data = json.load(f)
                self.app_token = data.get("app_token")
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save_token(self):
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            json.dump({"app_token": self.app_token, "saved_at": time.time()}, f)
        try:
            os.chmod(TOKEN_FILE, 0o600)  # token is a credential
        except Exception:
            pass

    # ── low-level HTTP helper ─────────────────────────────────────
    def _request(self, method, path, body=None, auth=True, timeout=5):
        url = FREEBOX_BASE + path
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        if auth and self.session_token:
            req.add_header("X-Fbx-App-Auth", self.session_token)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())

    # ── pairing (one-time) ────────────────────────────────────────
    def pair(self):
        """
        First-time pairing. Requires physical confirmation on the Freebox
        front-panel screen. Blocks up to ~60 seconds.
        """
        print("\n🔑 Starting pairing with Freebox...")
        resp = self._request("POST", "/api/v6/login/authorize/", {
            "app_id": APP_ID,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "device_name": DEVICE_NAME,
        }, auth=False)
        if not resp.get("success"):
            raise RuntimeError(f"authorize failed: {resp}")
        track_id = resp["result"]["track_id"]
        app_token = resp["result"]["app_token"]

        bar = "═" * 60
        print(f"\n{bar}")
        print("📺  GO TO YOUR FREEBOX NOW")
        print(bar)
        print("  Press ✓ (OK) on the Freebox front-panel screen")
        print("  to authorize 'FreeZap'.  You have ~60 seconds.")
        print(f"{bar}\n")

        # Poll until granted / denied / timeout
        for attempt in range(90):
            time.sleep(1)
            try:
                r = self._request("GET", f"/api/v6/login/authorize/{track_id}", auth=False)
            except Exception as e:
                print(f"  poll error: {e}")
                continue
            status = r.get("result", {}).get("status", "")
            if status == "granted":
                print("✅ Pairing granted — token saved!")
                self.app_token = app_token
                self._save_token()
                return True
            if status == "denied":
                raise RuntimeError("Pairing denied by user")
            if status == "timeout":
                raise RuntimeError("Pairing timed out on the Freebox side")
            if status == "unknown":
                raise RuntimeError("Pairing track lost (unknown)")
            # else: "pending" — keep polling
            if attempt % 5 == 0:
                print(f"  ... waiting ({attempt}s)")
        raise RuntimeError("Pairing timed out (agent side, 90s)")

    # ── session login (every 25 min) ──────────────────────────────
    def login(self):
        if not self.app_token:
            raise RuntimeError("No app_token stored. Run pairing first.")
        # 1. Get challenge
        r = self._request("GET", "/api/v6/login/", auth=False)
        challenge = r["result"]["challenge"]
        # 2. Compute HMAC-SHA1  (key=app_token, data=challenge)
        password = hmac.new(
            self.app_token.encode("utf-8"),
            challenge.encode("utf-8"),
            hashlib.sha1,
        ).hexdigest()
        # 3. Exchange for session_token
        r = self._request("POST", "/api/v6/login/session/", {
            "app_id": APP_ID,
            "password": password,
        }, auth=False)
        if not r.get("success"):
            err = r.get("error_code", "unknown")
            raise RuntimeError(f"session login failed: {err}")
        self.session_token = r["result"]["session_token"]
        self.session_expires_at = time.time() + SESSION_RENEW_SECONDS
        print("🔐 Session opened")

    def ensure_session(self):
        if not self.session_token or time.time() >= self.session_expires_at:
            self.login()

    # ── player discovery ──────────────────────────────────────────
    def discover_player(self):
        self.ensure_session()
        r = self._request("GET", "/api/v6/player/", auth=True)
        players = r.get("result", [])
        if not players:
            raise RuntimeError("No Freebox Player found on this box")
        # Pick the first one — most Freebox setups have a single Player
        self.player_id = players[0].get("id")
        label = players[0].get("device_name") or f"Player {self.player_id}"
        print(f"🎬 Discovered player: {label} (id={self.player_id})")
        return self.player_id

    # ── status queries ────────────────────────────────────────────
    def _player_get(self, sub_path):
        self.ensure_session()
        if not self.player_id:
            self.discover_player()
        path = f"/api/v6/player/{self.player_id}/api/v7{sub_path}"
        try:
            return self._request("GET", path)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                # Session expired — force re-login once
                self.session_token = None
                self.ensure_session()
                return self._request("GET", path)
            raise

    def get_status(self):
        r = self._player_get("/status/")
        result = r.get("result", {})
        power_state = result.get("power_state", "unknown")
        fg = result.get("foreground_app") or {}
        # Extract current channel if on TV
        channel = None
        if fg.get("package") == "fr.freebox.tv":
            ctx = fg.get("context") or {}
            ch = ctx.get("channel") or {}
            channel = ch.get("name") or ch.get("uuid")
        return {
            "powered": power_state == "running",
            "power_state": power_state,  # running | standby | unknown
            "channel": channel,
            "app": fg.get("package") or None,
        }

    def get_volume(self):
        try:
            r = self._player_get("/control/volume")
        except (urllib.error.HTTPError, urllib.error.URLError):
            return None  # Endpoint not exposed on Revolution
        result = r.get("result", {}) or {}
        return {
            "volume": result.get("volume"),
            "muted": result.get("muted"),
        }

    def poll(self):
        """One polling iteration. Updates self.last_status."""
        try:
            status = self.get_status()
            vol = self.get_volume()
            if vol:
                status.update(vol)
            status["agent_ok"] = True
            status["error"] = None
        except Exception as e:
            status = {
                "agent_ok": False,
                "powered": False,
                "error": f"{type(e).__name__}: {e}",
            }
        status["timestamp"] = time.time()
        with self.lock:
            self.last_status = status


# ─── Singleton ────────────────────────────────────────────────────
client = FreeboxClient()


def poll_loop():
    """Background polling thread."""
    while True:
        client.poll()
        time.sleep(POLL_INTERVAL)


# ─── HTTP Server ──────────────────────────────────────────────────
class AgentHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # quiet by default; errors still go to stderr

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status, data):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/health":
            self._json(200, {
                "ok": True,
                "paired": client.app_token is not None,
                "session_active": client.session_token is not None,
                "player_id": client.player_id,
                "agent_version": APP_VERSION,
            })
        elif path == "/status":
            with client.lock:
                snapshot = client.last_status or {
                    "agent_ok": False,
                    "error": "not polled yet",
                    "timestamp": time.time(),
                }
            self._json(200, snapshot)
        elif path == "/":
            self._json(200, {
                "agent": "freezap-agent",
                "version": APP_VERSION,
                "endpoints": ["/health", "/status"],
            })
        else:
            self._json(404, {"error": "not found", "path": path})


# ─── Main ─────────────────────────────────────────────────────────
def banner():
    print("═" * 60)
    print("  FreeZap Agent v" + APP_VERSION)
    print("  Freebox Revolution (v6) bridge — local HTTP bridge")
    print("═" * 60)


def main() -> int:
    banner()

    # 1. Pair if needed
    if not client.app_token:
        print("\n📡 No token found — starting first-time pairing.")
        try:
            client.pair()
        except Exception as e:
            print(f"\n❌ Pairing failed: {e}")
            return 1
    else:
        print(f"\n🔑 Token loaded from {TOKEN_FILE}")

    # 2. Open session + discover player
    try:
        client.login()
        client.discover_player()
    except Exception as e:
        print(f"\n❌ Initial login failed: {e}")
        print("   Your token may be stale. Delete ~/.freezap/token.json and re-run.")
        return 2

    # 3. Start polling thread
    t = threading.Thread(target=poll_loop, daemon=True, name="freezap-poll")
    t.start()

    # 4. Start HTTP server
    bar = "═" * 60
    print(f"\n{bar}")
    print(f"  ✅ FreeZap Agent running on http://localhost:{LISTEN_PORT}/")
    print(f"  Endpoints: /health  /status")
    print(f"  Press Ctrl+C to stop.")
    print(f"{bar}\n")

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    try:
        with socketserver.ThreadingTCPServer(("", LISTEN_PORT), AgentHandler) as srv:
            srv.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Agent stopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
