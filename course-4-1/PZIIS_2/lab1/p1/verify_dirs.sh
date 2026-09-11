#!/bin/bash
# П.16: чтение каталога, создание файла, удаление каждого существующего file*.
# Существующие файлы копируются, удаляются проверяемым uid и восстанавливаются.
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
printf 'user\tdir\tlist\tcreate\tdelete_existing\n' >> "${TSV}"

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
    bak="$(mktemp -d)"

    set +e
    if [[ ${user} == root ]]; then
      ls "${dpath}" &>/dev/null
      l_rc=$?
      touch "${dpath}/${probe}" 2>/dev/null
      c_rc=$?
      rm -f "${dpath}/${probe}" 2>/dev/null
    else
      runuser -u "${user}" -- ls "${dpath}" &>/dev/null
      l_rc=$?
      runuser -u "${user}" -- touch "${dpath}/${probe}" 2>/dev/null
      c_rc=$?
      rm -f "${dpath}/${probe}" 2>/dev/null || true
    fi

    # Удаление каждого существующего file* с последующим восстановлением
    shopt -s nullglob
    files=("${dpath}"/file*)
    shopt -u nullglob
    if ((${#files[@]})); then
      cp -a -- "${files[@]}" "${bak}/" 2>/dev/null
    fi
    failed=0
    if ((${#files[@]} == 0)); then
      failed=1
    else
      for f in "${files[@]}"; do
        if [[ ${user} == root ]]; then
          rm -f -- "${f}" 2>/dev/null || failed=1
        else
          runuser -u "${user}" -- rm -f -- "${f}" 2>/dev/null || failed=1
        fi
      done
    fi
    d_rc=${failed}
    if [[ -d ${bak} ]]; then
      cp -a -- "${bak}/." "${dpath}/" 2>/dev/null || true
      rm -rf "${bak}"
    fi
    set -e

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
