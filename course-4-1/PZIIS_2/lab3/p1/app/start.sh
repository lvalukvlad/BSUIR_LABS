#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -r requirements.txt
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

PORT="${LAB3_PORT:-5070}"
export LAB3_PORT="$PORT"
export LAB3_HOST="${LAB3_HOST:-127.0.0.1}"

if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
  sleep 0.3
fi

echo "http://127.0.0.1:${PORT}/"

if [[ -n "${DISPLAY:-}" ]] && command -v xdg-open >/dev/null 2>&1; then
  (sleep 1.2 && xdg-open "http://127.0.0.1:${PORT}/" >/dev/null 2>&1) &
fi

exec python app.py
