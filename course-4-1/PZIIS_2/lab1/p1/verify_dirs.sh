#!/bin/bash
# П.16: проверка каталогов — чтение содержимого, создание файла, удаление.
# Существующие file* не трогаются: запись/удаление только зонда .__probe_*
# Запуск: sudo ./verify_dirs.sh
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Ошибка: запускайте от root (sudo ./verify_dirs.sh)" >&2
  exit 1
fi

BASE="/home/pzs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${SCRIPT_DIR}/results"
mkdir -p "${OUT_DIR}"
TSV="${OUT_DIR}/verify_dirs.tsv"
TXT="${OUT_DIR}/verify_dirs.txt"

USERS=(iit11 iit12 iit21 iit22 iit3 root)
DIRS=(pzs11 pzs12 pzs13 pzs14 pzs15)

: > "${TSV}"
: > "${TXT}"
printf 'user\tdir\tlist\tcreate\tdelete_probe\n' >> "${TSV}"

yesno() { [[ $1 -eq 0 ]] && echo "ДА" || echo "НЕТ"; }

{
  echo "=== Проверка доступа к каталогам (п.16) ==="
  echo "Дата: $(date -Is)"
  echo
} | tee -a "${TXT}"

for user in "${USERS[@]}"; do
  echo "=== Пользователь: ${user} ===" | tee -a "${TXT}"
  for dir in "${DIRS[@]}"; do
    dpath="${BASE}/${dir}"
    probe=".__probe_${user}_$$"

    set +e
    if [[ ${user} == root ]]; then
      ls "${dpath}" &>/dev/null
      l_rc=$?
      touch "${dpath}/${probe}" 2>/dev/null
      c_rc=$?
      if [[ ${c_rc} -eq 0 ]]; then
        rm -f "${dpath}/${probe}" 2>/dev/null
        d_rc=$?
      else
        d_rc=1
      fi
    else
      runuser -u "${user}" -- ls "${dpath}" &>/dev/null
      l_rc=$?
      runuser -u "${user}" -- touch "${dpath}/${probe}" 2>/dev/null
      c_rc=$?
      if [[ ${c_rc} -eq 0 ]]; then
        runuser -u "${user}" -- rm -f "${dpath}/${probe}" 2>/dev/null
        d_rc=$?
      else
        d_rc=1
        rm -f "${dpath}/${probe}" 2>/dev/null
      fi
    fi
    set -e

    # Подчистка зонда на всякий случай
    rm -f "${dpath}/${probe}" 2>/dev/null || true

    l=$(yesno "${l_rc}")
    c=$(yesno "${c_rc}")
    d=$(yesno "${d_rc}")
    printf '  %-8s LIST=%-3s CREATE=%-3s DELETE=%-3s\n' "${dir}" "${l}" "${c}" "${d}" | tee -a "${TXT}"
    printf '%s\t%s\t%s\t%s\t%s\n' "${user}" "${dir}" "${l}" "${c}" "${d}" >> "${TSV}"
  done
  echo | tee -a "${TXT}"
done

echo "Результаты: ${TXT}"
echo "Таблица TSV: ${TSV}"
