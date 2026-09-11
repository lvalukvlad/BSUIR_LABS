#!/usr/bin/env bash
# Дамп предоставленного (небезопасного) варианта после create.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="${ROOT}/provided_app"
RES="${ROOT}/results"
mkdir -p "${RES}"
PORT="${LAB3_PROVIDED_PORT:-5071}"
BASE="http://127.0.0.1:${PORT}"

P1_VENV="/home/ubuntuuser/Desktop/BSUIR_LABS/course-4-1/PZIIS_2/lab3/p1/app/.venv"
if [[ -d "${P1_VENV}" ]]; then
  # shellcheck disable=SC1091
  source "${P1_VENV}/bin/activate"
fi

pkill -f "provided_app/app.py" 2>/dev/null || true
sleep 0.3
python "${APP}/app.py" >"${RES}/provided.log" 2>&1 &
PID=$!
echo "provided pid=${PID}" | tee "${RES}/provided_meta.txt"
for i in $(seq 1 30); do
  curl -fsS "${BASE}/health" >/dev/null 2>&1 && break
  sleep 0.3
done

curl -sS -X POST "${BASE}/secrets" -d "title=s&body=LAB3_SECRET_PLAIN_BRAVO" -o /dev/null
curl -sS -X POST "${BASE}/notes" -d "title=n&body=LAB3_PUBLIC_NOTE_ALPHA" -o /dev/null
sleep 0.4

DUMP_SCRIPT="/home/ubuntuuser/Desktop/BSUIR_LABS/course-4-1/PZIIS_2/lab3/p1/scripts/dump_and_analyze.sh"
OUT_DIR="${RES}/dumps"
mkdir -p "${OUT_DIR}"
# reuse dump script but write into p2 results: call gcore inline
WORKDIR="$(mktemp -d)"
(
  cd "${WORKDIR}"
  gcore -o core "${PID}"
  CORE="$(ls -1 core.* | head -1)"
  cp "${CORE}" "${OUT_DIR}/provided_after_create.bin"
)
strings -n 6 "${OUT_DIR}/provided_after_create.bin" > "${OUT_DIR}/provided_after_create_strings.txt"
{
  echo "provided dump after_create pid=${PID}"
  for m in LAB3_PUBLIC_NOTE_ALPHA LAB3_SECRET_PLAIN_BRAVO; do
    echo "marker ${m}: count=$(grep -F -c -- "$m" "${OUT_DIR}/provided_after_create_strings.txt" || true)"
  done
} | tee "${OUT_DIR}/provided_summary.txt"

echo "Provided scenario done (pid=${PID})."
