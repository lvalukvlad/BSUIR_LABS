#!/usr/bin/env bash
# Полный сценарий: поднять приложение, CRUD через HTTP, дампы after_create/update/delete.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="${ROOT}/app"
RES="${ROOT}/results"
mkdir -p "${RES}/dumps" "${RES}/profile"
chmod +x "${ROOT}/scripts/"*.sh

PORT="${LAB3_PORT:-5070}"
BASE="http://127.0.0.1:${PORT}"

if [[ ! -d "${APP_DIR}/.venv" ]]; then
  python3 -m venv "${APP_DIR}/.venv"
  # shellcheck disable=SC1091
  source "${APP_DIR}/.venv/bin/activate"
  pip install -q -r "${APP_DIR}/requirements.txt"
else
  # shellcheck disable=SC1091
  source "${APP_DIR}/.venv/bin/activate"
fi

pkill -f "${APP_DIR}/app.py" 2>/dev/null || true
sleep 0.5

python "${APP_DIR}/app.py" >"${RES}/app.log" 2>&1 &
APP_PID=$!
echo "app pid=${APP_PID}" | tee "${RES}/run_meta.txt"

for i in $(seq 1 30); do
  if curl -fsS "${BASE}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.3
done
curl -fsS "${BASE}/health" | tee "${RES}/health.json"
echo

# --- create ---
curl -sS -o /dev/null -w "note_create:%{http_code}\n" -X POST "${BASE}/notes" \
  -d "title=public&body=LAB3_PUBLIC_NOTE_ALPHA"
curl -sS -o /dev/null -w "secret_create:%{http_code}\n" -X POST "${BASE}/secrets" \
  -d "title=secret1&body=LAB3_SECRET_PLAIN_BRAVO"
sleep 0.5
"${ROOT}/scripts/dump_and_analyze.sh" "${APP_PID}" after_create

# --- update ---
curl -sS -o /dev/null -w "secret_update:%{http_code}\n" -X POST "${BASE}/secrets/1/update" \
  -d "title=secret1&body=LAB3_SECRET_UPDATED_DELTA"
curl -sS -o /dev/null -w "note_update:%{http_code}\n" -X POST "${BASE}/notes/1/update" \
  -d "title=public&body=LAB3_PUBLIC_NOTE_ALPHA"
sleep 0.5
"${ROOT}/scripts/dump_and_analyze.sh" "${APP_PID}" after_update

# --- delete ---
curl -sS -o /dev/null -w "secret_delete:%{http_code}\n" -X POST "${BASE}/secrets/1/delete"
curl -sS -o /dev/null -w "note_delete:%{http_code}\n" -X POST "${BASE}/notes/1/delete"
sleep 0.5
"${ROOT}/scripts/dump_and_analyze.sh" "${APP_PID}" after_delete

# --- profile snapshot ---
python3 - <<'PY' | tee "${RES}/profile/proc_status.txt"
import os, time
pid = int(open(os.environ.get("RES_PID_FILE", "/dev/null"), "r").read()) if False else None
PY

# get pid from meta
PID="$(awk -F= '/app pid=/{print $2}' "${RES}/run_meta.txt" | tr -d ' ')"
{
  echo "=== /proc/${PID}/status (Vm*) ==="
  grep -E '^(Name|Pid|VmPeak|VmSize|VmRSS|Threads)' "/proc/${PID}/status" || true
  echo
  echo "=== sample ps ==="
  ps -p "${PID}" -o pid,pcpu,pmem,rss,vsz,etime,cmd
} | tee "${RES}/profile/cpu_mem.txt"

# cProfile of a short client workload against running server
python3 - <<PY | tee "${RES}/profile/cprofile_client.txt"
import cProfile, pstats, io, requests
base = "${BASE}"
pr = cProfile.Profile()
pr.enable()
for _ in range(20):
    requests.get(base + "/health", timeout=2)
    requests.post(base + "/notes", data={"title": "t", "body": "b"}, timeout=2)
pr.disable()
s = io.StringIO()
pstats.Stats(pr, stream=s).sort_stats("cumtime").print_stats(15)
print(s.getvalue())
PY

# aggregate marker summary
{
  echo "Dump marker summary"
  echo "date: $(date -Iseconds)"
  echo
  for f in "${RES}/dumps"/core_*_summary.txt; do
    echo "----- $(basename "$f") -----"
    cat "$f"
    echo
  done
} | tee "${RES}/dumps/SUMMARY.txt"

echo "Scenario finished. App still running pid=${PID} (stop: kill ${PID})"
