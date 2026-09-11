#!/bin/bash
# П.14: проверка чтения / записи / исполнения файлов для каждого пользователя.
# Запись — проба с откатом содержимого. Исполнение — реальный запуск с тайм-аутом.
# Запуск: sudo ./verify_files.sh
# Результаты: ./results/verify_files.tsv и ./results/verify_files.txt
set -uo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Ошибка: запускайте от root (sudo ./verify_files.sh)" >&2
  exit 1
fi

# Ожидаемые отказы доступа не должны ронять скрипт
set +e

BASE="/home/pzs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${SCRIPT_DIR}/results"
mkdir -p "${OUT_DIR}"
TSV="${OUT_DIR}/verify_files.tsv"
TXT="${OUT_DIR}/verify_files.txt"

USERS=(iit11 iit12 iit21 iit22 iit3 root)
DIRS=(pzs11 pzs12 pzs13 pzs14 pzs15)
FILES=(
  file11 file12 file13 file14 file15
  file21 file22 file23 file24 file25
  file31 file32 file33 file34 file35
  file41 file42 file43 file44 file45
  file51 file52 file53 file54 file55
)

: > "${TSV}"
: > "${TXT}"
printf 'user\tdir\tfile\tread\twrite\texecute\n' >> "${TSV}"

yesno() { [[ $1 -eq 0 ]] && echo "ДА" || echo "НЕТ"; }

check_read() {
  local user="$1" path="$2"
  if [[ ${user} == root ]]; then
    cat "${path}" &>/dev/null
  else
    runuser -u "${user}" -- cat "${path}" &>/dev/null
  fi
}

check_write() {
  local user="$1" path="$2"
  local backup marker rc=1
  marker="__probe_write_$$_${RANDOM}__"
  backup="$(mktemp)"
  if ! cp -a -- "${path}" "${backup}" 2>/dev/null; then
    rm -f "${backup}"
    return 1
  fi

  if [[ ${user} == root ]]; then
    printf '\n%s\n' "${marker}" >> "${path}" 2>/dev/null
    rc=$?
  else
    runuser -u "${user}" -- bash -c "printf '\\n%s\\n' '${marker}' >> '${path}'" 2>/dev/null
    rc=$?
  fi

  cp -a -- "${backup}" "${path}" 2>/dev/null || true
  rm -f "${backup}"
  return "${rc}"
}

check_exec() {
  local user="$1" path="$2"
  # Реальный запуск, не test -x: скрипту с shebang нужно ещё и чтение.
  # filex5 делает read — подаём пустую строку и ограничиваем время.
  if [[ ${user} == root ]]; then
    timeout 1s bash -c 'printf "\n" | "$1"' _ "${path}" &>/dev/null
  else
    timeout 1s runuser -u "${user}" -- bash -c 'printf "\n" | "$1"' _ "${path}" &>/dev/null
  fi
}

{
echo "=== Проверка доступа к файлам (п.14) ==="
echo "Дата: $(date -Is)"
echo "EXEC: реальный запуск скрипта (нужны биты x и чтения для shebang)"
  echo
} | tee -a "${TXT}"

for user in "${USERS[@]}"; do
  echo "=== Пользователь: ${user} ===" | tee -a "${TXT}"
  for dir in "${DIRS[@]}"; do
    dpath="${BASE}/${dir}"
    if [[ ! -d ${dpath} ]]; then
      echo "  [пропуск] нет каталога ${dpath}" | tee -a "${TXT}"
      continue
    fi
    for file in "${FILES[@]}"; do
      fpath="${dpath}/${file}"
      if [[ ! -e ${fpath} ]]; then
        printf '  %-8s %-6s READ=— WRITE=— EXEC=— (нет файла)\n' "${dir}" "${file}" | tee -a "${TXT}"
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "${user}" "${dir}" "${file}" "—" "—" "—" >> "${TSV}"
        continue
      fi

      set +e
      check_read "${user}" "${fpath}"
      r_rc=$?
      check_write "${user}" "${fpath}"
      w_rc=$?
      check_exec "${user}" "${fpath}"
      x_rc=$?
      set -e

      r=$(yesno "${r_rc}")
      w=$(yesno "${w_rc}")
      x=$(yesno "${x_rc}")

      printf '  %-8s %-6s READ=%-3s WRITE=%-3s EXEC=%-3s\n' "${dir}" "${file}" "${r}" "${w}" "${x}" | tee -a "${TXT}"
      printf '%s\t%s\t%s\t%s\t%s\t%s\n' "${user}" "${dir}" "${file}" "${r}" "${w}" "${x}" >> "${TSV}"
    done
  done
  echo | tee -a "${TXT}"
done

echo "Результаты: ${TXT}"
echo "Таблица TSV: ${TSV}"
