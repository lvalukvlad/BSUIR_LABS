#!/usr/bin/env bash
# Снятие дампа ОЗУ процесса и поиск маркеров.
# Запуск: ./dump_and_analyze.sh <pid> <label>
set -euo pipefail

PID="${1:?usage: $0 <pid> <label>}"
LABEL="${2:?usage: $0 <pid> <label>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT}/results/dumps"
mkdir -p "${OUT_DIR}"

STAMP="$(date +%Y%m%d_%H%M%S)"
CORE_PREFIX="${OUT_DIR}/core_${LABEL}_${STAMP}"

echo "==> gcore pid=${PID} label=${LABEL}"
WORKDIR="$(mktemp -d)"
cleanup() { rm -rf "${WORKDIR}"; }
trap cleanup EXIT

(
  cd "${WORKDIR}"
  gcore -o core "${PID}"
  CORE_FILE="$(ls -1 core.* | head -1)"
  cp "${CORE_FILE}" "${CORE_PREFIX}.bin"
)

BIN="${CORE_PREFIX}.bin"
REP="${CORE_PREFIX}_strings.txt"
SUMMARY="${CORE_PREFIX}_summary.txt"

echo "==> strings -> ${REP}"
strings -n 6 "${BIN}" > "${REP}" || true

MARKERS=(
  "LAB3_PUBLIC_NOTE_ALPHA"
  "LAB3_SECRET_PLAIN_BRAVO"
  "LAB3_SECRET_PLAIN_CHARLIE"
  "LAB3_SECRET_UPDATED_DELTA"
)

{
  echo "dump: ${BIN}"
  echo "pid: ${PID}"
  echo "label: ${LABEL}"
  echo "time: ${STAMP}"
  echo
  for m in "${MARKERS[@]}"; do
    cnt="$(grep -F -c -- "${m}" "${REP}" || true)"
    echo "marker ${m}: count=${cnt}"
  done
} | tee "${SUMMARY}"

echo "==> done: ${SUMMARY}"
