#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# FreeZap — local HTTP server
#
# Serves FreeZap over plain HTTP on your LAN so phones on the same
# Wi-Fi can use it without hitting the GitHub Pages / HTTPS mixed-
# content block.
#
# Usage:
#   ./serve.sh           # serve on port 8000
#   ./serve.sh 9000      # serve on port 9000
# ═══════════════════════════════════════════════════════════════════
set -e
cd "$(dirname "$0")"

PORT="${1:-8000}"

# Find the LAN IP of the primary active interface.
# Try en0 (Wi-Fi) first, then en1 (Ethernet), then fall back to hostname.
IP=""
if command -v ipconfig >/dev/null 2>&1; then
  IP="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"
fi
if [ -z "$IP" ] && command -v hostname >/dev/null 2>&1; then
  IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
fi

echo ""
echo "  📺  FreeZap — local HTTP server"
echo "  ─────────────────────────────────"
echo ""
if [ -n "$IP" ]; then
  echo "  📱  On your phone (same Wi-Fi):"
  echo ""
  echo "      http://${IP}:${PORT}/"
  echo ""
  echo "      → tap 'Add to Home Screen' in Safari / Chrome"
  echo ""
fi
echo "  💻  On this machine:"
echo ""
echo "      http://localhost:${PORT}/"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

# Prefer python3, fall back to python
if command -v python3 >/dev/null 2>&1; then
  exec python3 -m http.server "$PORT"
elif command -v python >/dev/null 2>&1; then
  exec python -m SimpleHTTPServer "$PORT"
else
  echo "  ❌  Neither python3 nor python is installed."
  echo "      Install Python, or run any other static HTTP server from this folder."
  exit 1
fi
