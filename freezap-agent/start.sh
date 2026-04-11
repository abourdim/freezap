#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# FreeZap Agent launcher
#
# Usage:
#   ./start.sh            # runs on port 8766 (default)
#   FREEZAP_AGENT_PORT=9000 ./start.sh
# ═══════════════════════════════════════════════════════════════════
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Install Python 3.6+ and try again."
  exit 1
fi

exec python3 freezap-agent.py
