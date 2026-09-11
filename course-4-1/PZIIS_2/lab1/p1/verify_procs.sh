#!/bin/bash
# П.15: запуск файлов шаблона filex5 от iit11 и проверка, кто может остановить процесс.
# Запуск: sudo ./verify_procs.sh
set -uo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Ошибка: запускайте от root (sudo ./verify_procs.sh)" >&2
  exit 1
fi

BASE="/home/pzs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${SCRIPT_DIR}/results"
mkdir -p "${OUT_DIR}"
TSV="${OUT_DIR}/verify_procs.tsv"
TXT="${OUT_DIR}/verify_procs.txt"

USERS=(iit11 iit12 iit21 iit22 iit3 root)
DIR="${BASE}/pzs14"
TARGETS=(file15 file25 file35 file45 file55)

: > "${TSV}"
: > "${TXT}"
printf 'file\tstarter\tpid\tkiller\tkill_ok\n' >> "${TSV}"

{
  echo "=== Проверка остановки процессов filex5 (п.15) ==="
  echo "Дата: $(date -Is)"
  echo "Каталог: ${DIR}"
  echo
} | tee -a "${TXT}"

WORK="$(mktemp -d)"
PIDS_TO_CLEAN=()

cleanup() {
  local p
  for p in "${PIDS_TO_CLEAN[@]:-}"; do
    kill -KILL "${p}" 2>/dev/null || true
  done
  pkill -u iit11 -f "${WORK}" 2>/dev/null || true
  rm -rf "${WORK}"
}
trap cleanup EXIT

# Долгоживущие обёртки (содержимое filex5 + sleep), запуск от iit11
for f in "${TARGETS[@]}"; do
  src="${DIR}/${f}"
  if [[ ! -f ${src} ]]; then
    echo "Пропуск ${f}: нет файла ${src}" | tee -a "${TXT}"
    continue
  fi
  cat > "${WORK}/${f}.run" <<EOF
#!/bin/bash
$(sed -n '2p' "${src}" 2>/dev/null || true)
sleep 300
EOF
  chmod 755 "${WORK}/${f}.run"
  chown iit11:group_iit1 "${WORK}/${f}.run"
done
chmod 755 "${WORK}"
chown iit11:group_iit1 "${WORK}"

start_proc() {
  local f="$1"
  local runner="${WORK}/${f}.run"
  local pidfile="${WORK}/${f}.pid"
  rm -f "${pidfile}"
  # setsid + nohup: процесс не умирает при выходе оболочки runuser
  runuser -u iit11 -- bash -c "nohup setsid '${runner}' >/dev/null 2>&1 & echo \$! > '${pidfile}'"
  sleep 0.3
  if [[ ! -s ${pidfile} ]]; then
    echo ""
    return 1
  fi
  local pid
  pid="$(tr -d '[:space:]' < "${pidfile}")"
  # Убедимся, что это живой процесс пользователя iit11
  if ! kill -0 "${pid}" 2>/dev/null; then
    echo ""
    return 1
  fi
  echo "${pid}"
}

for f in "${TARGETS[@]}"; do
  runner="${WORK}/${f}.run"
  [[ -f ${runner} ]] || continue

  echo "--- Файл ${f} ---" | tee -a "${TXT}"

  for killer in "${USERS[@]}"; do
    pid="$(start_proc "${f}" || true)"
    if [[ -z ${pid} ]] || ! kill -0 "${pid}" 2>/dev/null; then
      echo "  [${killer}] не удалось запустить процесс от iit11" | tee -a "${TXT}"
      printf '%s\tiit11\t-\t%s\tНЕТ_ЗАПУСКА\n' "${f}" "${killer}" >> "${TSV}"
      continue
    fi
    PIDS_TO_CLEAN+=("${pid}")
    echo "  PID=${pid}; попытка kill от ${killer}" | tee -a "${TXT}"

    kc=1
    if [[ ${killer} == root ]]; then
      kill -TERM "${pid}" 2>/dev/null && kc=0 || kc=$?
    else
      runuser -u "${killer}" -- kill -TERM "${pid}" 2>/dev/null && kc=0 || kc=$?
    fi
    sleep 0.25

    if [[ ${kc} -eq 0 ]] && ! kill -0 "${pid}" 2>/dev/null; then
      echo "  kill от ${killer}: ДА" | tee -a "${TXT}"
      printf '%s\tiit11\t%s\t%s\tДА\n' "${f}" "${pid}" "${killer}" >> "${TSV}"
    else
      echo "  kill от ${killer}: НЕТ" | tee -a "${TXT}"
      printf '%s\tiit11\t%s\t%s\tНЕТ\n' "${f}" "${pid}" "${killer}" >> "${TSV}"
      kill -KILL "${pid}" 2>/dev/null || true
    fi
  done
  echo | tee -a "${TXT}"
done

echo "Результаты: ${TXT}"
echo "Таблица TSV: ${TSV}"
