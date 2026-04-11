# 📡 FreeZap Agent

> Local HTTP bridge between **FreeZap** (browser) and the authenticated
> **Freebox OS API**. Reads real-time Player status (powered, current channel,
> volume) and exposes it on `http://localhost:8766/` with CORS so FreeZap can
> poll it.

Without this agent, FreeZap only knows *"the Freebox responds on the LAN"*.
With the agent, FreeZap shows:

- 🟢 **`📺 TF1`** — Player running, on channel TF1
- 😴 **`En veille`** — Player in standby
- 🔴 **`Injoignable`** — Agent down or Freebox unreachable
- 🔊 **`Vol 42`** — if the volume endpoint is exposed by your Revolution

## Requirements

| Thing | Version |
|---|---|
| Python | 3.6 or later (pre-installed on macOS and most Linux distros) |
| Freebox Player | **Revolution (v6)** — the big black box with an LCD screen |
| Network | Your machine and the Freebox on the same LAN |
| Permissions | Physical access to the Freebox (one-time pairing) |

No pip install, no virtualenv, no dependencies — the agent uses only the
Python stdlib (`http.server`, `hashlib`, `hmac`, `urllib.request`, `json`,
`socketserver`).

## Quick start

### First time (pairing)

```bash
cd freezap-agent
./start.sh
```

The agent will:

1. Ask the Freebox OS API for an `app_token` (via `POST /api/v6/login/authorize`).
2. Print a big banner asking you to go physically to the Freebox.
3. **Go to the Freebox and press ✓ (OK) on the front-panel screen** within ~60 seconds.
4. Save the token to `~/.freezap/token.json` with mode 0600.

After that, the agent opens a session with HMAC-SHA1 and starts polling the
Player status every 2 seconds. FreeZap can then poll `http://localhost:8766/status`.

### Subsequent runs

```bash
./start.sh
```

That's it. The saved token is reused, no re-pairing needed.

## Endpoints

### `GET /health`

```json
{
  "ok": true,
  "paired": true,
  "session_active": true,
  "player_id": "1",
  "agent_version": "1.1.0"
}
```

### `GET /status`

```json
{
  "powered": true,
  "power_state": "running",
  "channel": "TF1",
  "app": "fr.freebox.tv",
  "volume": 42,
  "muted": false,
  "agent_ok": true,
  "timestamp": 1712844000.123
}
```

Field notes:

- `power_state` is `running` / `standby` / `unknown`.
- `channel` is `null` when the Player is not on the TV app.
- `volume` / `muted` may be `undefined` if your Revolution firmware does not
  expose `/control/volume` (the official Freebox Revolution API docs mark this
  endpoint as present but "not yet available for Freebox Revolution").
- `agent_ok: false` means the last poll failed — see the `error` field for details.

## Port

Default: `8766`. Override with the `FREEZAP_AGENT_PORT` env var:

```bash
FREEZAP_AGENT_PORT=9000 ./start.sh
```

## Running as a service (optional)

### macOS — launchd

Create `~/Library/LaunchAgents/com.freezap.agent.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.freezap.agent</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/YOUR_USER/path/to/freezap-agent/freezap-agent.py</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/freezap-agent.log</string>
  <key>StandardErrorPath</key><string>/tmp/freezap-agent.err</string>
</dict>
</plist>
```

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.freezap.agent.plist
```

### Linux / Raspberry Pi — systemd

Create `/etc/systemd/system/freezap-agent.service`:

```ini
[Unit]
Description=FreeZap Agent — Freebox OS API bridge
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/freezap-agent
ExecStart=/usr/bin/python3 /home/pi/freezap-agent/freezap-agent.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

Enable:

```bash
sudo systemctl enable --now freezap-agent
```

## Security

The **`app_token`** stored in `~/.freezap/token.json` is a long-lived credential
that grants control of your Freebox Player. The file is created with mode `0600`
(read/write for your user only). **Do not commit it, share it, or upload it anywhere.**

If you suspect the token is compromised:

1. Log into Freebox OS (`http://mafreebox.freebox.fr`)
2. Go to **Paramètres de la Freebox → Gestion des accès → Applications**
3. Revoke the "FreeZap" application
4. Delete `~/.freezap/token.json`
5. Run `./start.sh` again and re-pair

## Architecture

```
  FreeZap (browser)
    ├─ polls GET http://localhost:8766/status  (CORS allowed)
    └─ sends POST /key/<name>                  (future — not in v1.1.0)

  FreeZap Agent (this process)
    ├─ every 2 s: GET /api/v6/player/{id}/api/v7/status/  →  cache
    ├─ every 2 s: GET /api/v6/player/{id}/api/v7/control/volume  →  cache
    ├─ every 25 min: POST /api/v6/login/session/ (HMAC-SHA1 refresh)
    └─ HTTP server on :8766 with CORS headers

  Freebox Server (mafreebox.freebox.fr)
    └─ Freebox OS API  (HTTP, auth required)
```

## Troubleshooting

### "No token found — starting first-time pairing" but the Freebox screen shows nothing

- Check that you are on the **same LAN** as the Freebox.
- Verify `http://mafreebox.freebox.fr/` loads in your browser.
- The authorize call may have failed — re-run and watch the agent's stderr.

### "session login failed: auth_required" or 403 errors during polling

- The token was revoked from Freebox OS. Delete `~/.freezap/token.json` and re-pair.

### "No Freebox Player found on this box"

- You have a Freebox Server without a Player, or the Player is unplugged.
- FreeZap and this agent only make sense with a Freebox Revolution Player.

### `/control/volume` returns 404 / "not found"

- Known limitation on Freebox Revolution — the volume endpoint is documented
  but not implemented on all firmware versions. The agent silently reports
  `volume: null` in that case, which FreeZap handles gracefully.

## License

MIT — same as FreeZap.
