#!/bin/bash
# Часть 2: установка PostgreSQL.
# Запуск: sudo ./install.sh
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Ошибка: запускайте от root (sudo ./install.sh)" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "==> Обновление индексов пакетов"
apt-get update -y

echo "==> Установка PostgreSQL"
apt-get install -y postgresql postgresql-contrib

echo "==> Запуск службы"
if command -v systemctl &>/dev/null; then
  systemctl enable postgresql
  systemctl start postgresql
else
  service postgresql start
fi

echo "==> Версия:"
sudo -u postgres psql -c "SELECT version();" || true

echo "Установка завершена. Дальше: sudo ./setup_acl.sh"
