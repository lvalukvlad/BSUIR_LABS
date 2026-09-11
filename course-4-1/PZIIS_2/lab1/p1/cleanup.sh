#!/bin/bash
# П.17: удаление файлов, каталогов, пользователей и групп лабораторной.
# Запуск: sudo ./cleanup.sh
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Ошибка: запускайте от root (sudo ./cleanup.sh)" >&2
  exit 1
fi

BASE="/home/pzs"

echo "==> Удаление ${BASE}"
rm -rf "${BASE}"

echo "==> Удаление пользователей"
for u in iit11 iit12 iit21 iit22 iit3; do
  if id "${u}" &>/dev/null; then
    userdel -r "${u}" 2>/dev/null || userdel "${u}"
    echo "  удалён ${u}"
  fi
done

echo "==> Удаление групп"
for g in group_iit1 group_iit2; do
  if getent group "${g}" &>/dev/null; then
    groupdel "${g}" 2>/dev/null || echo "  не удалось удалить ${g} (возможно, ещё используется)"
    echo "  удалена ${g}"
  fi
done

echo "==> Очистка завершена"
