#!/bin/bash
# Лабораторная №1, часть 1: создание пользователей, каталогов и файлов с ACL (chmod/chown).
# Запуск: sudo ./setup.sh
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Ошибка: скрипт нужно запускать от root (sudo ./setup.sh)" >&2
  exit 1
fi

BASE="/home/pzs"

echo "==> Создание групп"
groupadd -f group_iit1
groupadd -f group_iit2

echo "==> Создание пользователей"
id iit11 &>/dev/null || useradd -m -G group_iit1 iit11
id iit12 &>/dev/null || useradd -m -G group_iit1 iit12
id iit21 &>/dev/null || useradd -m -G group_iit2 iit21
id iit22 &>/dev/null || useradd -m -G group_iit2 iit22
id iit3  &>/dev/null || useradd -m iit3

usermod -G group_iit1 iit11
usermod -G group_iit1 iit12
usermod -G group_iit2 iit21
usermod -G group_iit2 iit22

echo "==> Административные привилегии для iit21"
if getent group sudo &>/dev/null; then
  usermod -aG sudo iit21
elif getent group wheel &>/dev/null; then
  usermod -aG wheel iit21
else
  echo "Предупреждение: группы sudo/wheel нет — добавьте iit21 в sudoers вручную" >&2
fi

echo "==> Создание каталога ${BASE}"
mkdir -p "${BASE}"

# Unix DAC: права владельца проверяются раньше групповых.
# Каталоги «только группа/остальные» не должны принадлежать тестируемому владельцу iit11.
echo "==> Создание подкаталогов"
mkdir -p "${BASE}/pzs11" "${BASE}/pzs12" "${BASE}/pzs13" "${BASE}/pzs14" "${BASE}/pzs15"

chown iit11:group_iit1 "${BASE}/pzs11"
chmod 700 "${BASE}/pzs11"

chown root:group_iit1 "${BASE}/pzs12"
chmod 070 "${BASE}/pzs12"

chown root:root "${BASE}/pzs13"
chmod 007 "${BASE}/pzs13"

chown iit11:group_iit1 "${BASE}/pzs14"
chmod 777 "${BASE}/pzs14"

chown root:root "${BASE}/pzs15"
chmod 700 "${BASE}/pzs15"

# Вспомогательный скрипт создания файлов (выполняется от нужного uid)
CREATE_HELPER="$(mktemp)"
cat > "${CREATE_HELPER}" <<'HELPER'
#!/bin/bash
set -euo pipefail
dir="$1"
specs=(
  "file11:400" "file12:600" "file13:200" "file14:700" "file15:100"
  "file21:040" "file22:060" "file23:020" "file24:070" "file25:010"
  "file31:004" "file32:006" "file33:002" "file34:007" "file35:001"
  "file41:444" "file42:666" "file43:222" "file44:777" "file45:111"
  "file51:400" "file52:600" "file53:200" "file54:700" "file55:100"
)
for spec in "${specs[@]}"; do
  f="${spec%%:*}"
  mode="${spec##*:}"
  # Shebang нужен, чтобы ядро могло исполнить файл при бите +x
  {
    printf '#!/bin/bash\n'
    if [[ ${f} =~ ^file[1-5]5$ ]]; then
      # filex5: по методичке + короткий sleep для п.15 (если запускают оригинал)
      printf 'read testVariable\n'
    else
      printf 'echo "Hello World"\n'
    fi
  } > "${dir}/${f}"
  chmod "${mode}" "${dir}/${f}"
done
for f in file21 file22 file23 file24 file25; do
  chown :group_iit1 "${dir}/${f}" 2>/dev/null || true
done
HELPER
chmod 755 "${CREATE_HELPER}"

echo "==> Создание файлов от имени iit11 в pzs11–pzs14"
for d in pzs11 pzs12 pzs13 pzs14; do
  runuser -u iit11 -- "${CREATE_HELPER}" "${BASE}/${d}"
done

echo "==> Создание файлов в pzs15 от root"
bash "${CREATE_HELPER}" "${BASE}/pzs15"

rm -f "${CREATE_HELPER}"

echo "==> Передача file5[1-5] администратору (root) в pzs11–pzs14"
for d in pzs11 pzs12 pzs13 pzs14; do
  for f in file51 file52 file53 file54 file55; do
    chown root:root "${BASE}/${d}/${f}"
  done
done
chown -R root:root "${BASE}/pzs15"
chmod 700 "${BASE}/pzs15"

echo "==> Готово."
ls -la "${BASE}"
echo "Файлов в pzs11: $(find "${BASE}/pzs11" -maxdepth 1 -type f | wc -l)"
echo
echo "Дальше: sudo ./verify_files.sh && sudo ./verify_procs.sh && sudo ./verify_dirs.sh"
echo "Очистка:  sudo ./cleanup.sh"
