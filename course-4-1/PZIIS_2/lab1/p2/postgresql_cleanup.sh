#!/bin/bash
# Скрипт удаления postgresql_cleanup.sh

if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root"
   exit 1
fi

echo "Удаление базы данных и пользователей PostgreSQL..."
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS lab_db;
DROP USER IF EXISTS admin_user;
DROP USER IF EXISTS app_user;
DROP USER IF EXISTS guest_user;
DROP ROLE IF EXISTS admin_role;
DROP ROLE IF EXISTS user_role;
DROP ROLE IF EXISTS guest_role;
EOF

echo "Удаление пакетов PostgreSQL..."
apt-get purge -y postgresql postgresql-contrib
apt-get autoremove -y

echo "Очистка завершена."
