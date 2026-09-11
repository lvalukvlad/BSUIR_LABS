#!/bin/bash
# Часть 2: удаление объектов лабораторной в PostgreSQL.
# Запуск: sudo ./cleanup.sh [--purge]
#   --purge  — дополнительно удалить пакеты PostgreSQL
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Ошибка: запускайте от root (sudo ./cleanup.sh)" >&2
  exit 1
fi

PURGE=0
[[ ${1:-} == --purge ]] && PURGE=1

echo "==> Удаление БД и ролей"
sudo -u postgres psql <<'EOF'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'lab_db' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS lab_db;
DROP ROLE IF EXISTS admin_user;
DROP ROLE IF EXISTS app_user;
DROP ROLE IF EXISTS guest_user;
DROP ROLE IF EXISTS admin_role;
DROP ROLE IF EXISTS user_role;
DROP ROLE IF EXISTS guest_role;
EOF

# Восстановление pg_hba при наличии бэкапа
PG_HBA="$(sudo -u postgres psql -tA -c "SHOW hba_file;" 2>/dev/null | tr -d '[:space:]' || true)"
if [[ -n ${PG_HBA} && -f ${PG_HBA}.lab1.bak ]]; then
  echo "==> Восстановление ${PG_HBA} из .lab1.bak"
  cp -a "${PG_HBA}.lab1.bak" "${PG_HBA}"
  if command -v systemctl &>/dev/null; then
    systemctl reload postgresql 2>/dev/null || true
  fi
fi

if [[ ${PURGE} -eq 1 ]]; then
  echo "==> Удаление пакетов PostgreSQL (--purge)"
  export DEBIAN_FRONTEND=noninteractive
  apt-get purge -y 'postgresql*' || true
  apt-get autoremove -y || true
fi

echo "==> Очистка завершена"
