#!/usr/bin/env bash
#
# Start CR Process Automation on Linux / macOS (and a Linux VM or WSL2 guest
# running inside a Windows host).
#
#   * Picks Gunicorn automatically (falls back to Waitress if unavailable).
#   * Runs migrations and collects static files first.
#   * Wraps the process in a virtual X display (Xvfb) when no DISPLAY exists,
#     because the Playwright automation launches a non-headless Chromium.
#
# Usage:
#   ./start.sh                       # bind 0.0.0.0:8000
#   ./start.sh --host 127.0.0.1      # behind nginx on the same machine
#   ./start.sh --port 9000 --threads 16
#   NO_XVFB=1 ./start.sh             # skip the virtual display wrapper
#
set -euo pipefail
cd "$(dirname "$0")"

# Prefer the project virtualenv if present.
PY="${PYTHON:-python3}"
if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
elif [ -x "venv/bin/python" ]; then
  PY="venv/bin/python"
fi

CMD=("$PY" wsgi_app.py --migrate --collectstatic "$@")

# Playwright runs a non-headless browser; give it a display on headless hosts.
if [ "${NO_XVFB:-0}" != "1" ] && [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
  echo "[start] No DISPLAY found - running under xvfb-run (virtual display)."
  exec xvfb-run -a "${CMD[@]}"
fi

if [ "${NO_XVFB:-0}" != "1" ] && [ -z "${DISPLAY:-}" ]; then
  echo "[warn] No DISPLAY and xvfb-run not installed."
  echo "[warn] The web app will serve, but Playwright browser tasks may fail."
  echo "[warn] Install a virtual display, e.g.  sudo apt-get install -y xvfb"
fi

exec "${CMD[@]}"
