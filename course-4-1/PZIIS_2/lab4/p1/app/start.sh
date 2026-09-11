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

ROOT="$(cd .. && pwd)"
export LAB4_LOG_DIR="${LAB4_LOG_DIR:-$ROOT/logs}"
export LAB4_KEY_DIR="${LAB4_KEY_DIR:-$ROOT/keys}"
export LAB4_HTTP_HOST="${LAB4_HTTP_HOST:-0.0.0.0}"
export LAB4_HTTP_PORT="${LAB4_HTTP_PORT:-8088}"
mkdir -p "$LAB4_LOG_DIR" "$LAB4_KEY_DIR"

HTTP_PORT="${LAB4_HTTP_PORT}"
SSH_PORT="${LAB4_SSH_PORT:-2222}"

if command -v fuser >/dev/null 2>&1; then
  fuser -k "${HTTP_PORT}/tcp" 2>/dev/null || true
  fuser -k "${SSH_PORT}/tcp" 2>/dev/null || true
  sleep 0.3
fi

python ../ssh/server.py >>"$LAB4_LOG_DIR/ssh.out" 2>&1 &
echo $! > "$LAB4_LOG_DIR/ssh.pid"

echo "http://127.0.0.1:${HTTP_PORT}/"
echo "ssh://127.0.0.1:${SSH_PORT}/"

if [[ -n "${DISPLAY:-}" ]] && command -v xdg-open >/dev/null 2>&1; then
  (sleep 1.2 && xdg-open "http://127.0.0.1:${HTTP_PORT}/" >/dev/null 2>&1) &
fi

exec python app.py
