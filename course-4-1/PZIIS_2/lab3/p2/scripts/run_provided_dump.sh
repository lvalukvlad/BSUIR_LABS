#!/usr/bin/env bash
# Дампы предоставленного варианта: after_create / after_update / after_delete.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
P1_ROOT="$(cd "${ROOT}/../p1" && pwd)"
APP="${ROOT}/provided_app"
RES="${ROOT}/results"
OUT_DIR="${RES}/dumps"
mkdir -p "${RES}" "${OUT_DIR}"
PORT="${LAB3_PROVIDED_PORT:-5071}"
BASE="http://127.0.0.1:${PORT}"

P1_VENV="${P1_ROOT}/app/.venv"
if [[ -d "${P1_VENV}" ]]; then
  # shellcheck disable=SC1091
  source "${P1_VENV}/bin/activate"
fi

pkill -f "lab3/p2/provided_app/app.py" 2>/dev/null || true
sleep 0.3
python "${APP}/app.py" >"${RES}/provided.log" 2>&1 &
PID=$!
echo "provided pid=${PID}" | tee "${RES}/provided_meta.txt"
for i in $(seq 1 30); do
  curl -fsS "${BASE}/health" >/dev/null 2>&1 && break
  sleep 0.3
done

dump_now() {
  local label="$1"
  local workdir
  workdir="$(mktemp -d)"
  (
    cd "${workdir}"
    gcore -o core "${PID}"
    CORE="$(ls -1 core.* | head -1)"
    cp "${CORE}" "${OUT_DIR}/provided_${label}.bin"
  )
  rm -rf "${workdir}"
  strings -n 6 "${OUT_DIR}/provided_${label}.bin" > "${OUT_DIR}/provided_${label}_strings.txt"
  {
    echo "provided dump ${label} pid=${PID}"
    for m in LAB3_PUBLIC_NOTE_ALPHA LAB3_SECRET_PLAIN_BRAVO LAB3_SECRET_UPDATED_DELTA; do
      echo "marker ${m}: count=$(grep -F -c -- "$m" "${OUT_DIR}/provided_${label}_strings.txt" || true)"
    done
  } | tee "${OUT_DIR}/provided_${label}_summary.txt"
}

curl -sS -X POST "${BASE}/secrets" -d "title=s&body=LAB3_SECRET_PLAIN_BRAVO" -o /dev/null
curl -sS -X POST "${BASE}/notes" -d "title=n&body=LAB3_PUBLIC_NOTE_ALPHA" -o /dev/null
sleep 0.4
dump_now after_create

curl -sS -X POST "${BASE}/secrets/1/update" -d "title=s&body=LAB3_SECRET_UPDATED_DELTA" -o /dev/null
sleep 0.4
dump_now after_update

curl -sS -X POST "${BASE}/secrets/1/delete" -o /dev/null
sleep 0.4
dump_now after_delete

{
  echo "provided dump summaries"
  cat "${OUT_DIR}/provided_after_create_summary.txt"
  echo
  cat "${OUT_DIR}/provided_after_update_summary.txt"
  echo
  cat "${OUT_DIR}/provided_after_delete_summary.txt"
} | tee "${OUT_DIR}/provided_summary.txt"

echo "Provided scenario done (pid=${PID})."
