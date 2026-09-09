#!/bin/bash

# Скрипт необходимо запускать с правами root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root"
   exit 1
fi

# --- 1. Установка PostgreSQL ---
echo "Обновление списка пакетов и установка PostgreSQL..."
apt-get update
apt-get install -y postgresql postgresql-contrib

# Запуск службы
systemctl start postgresql
systemctl enable postgresql

# --- 2. Настройка ролей и прав доступа ---
# Переключаемся на пользователя postgres для выполнения SQL-команд
echo "Настройка ролей и прав доступа в PostgreSQL..."

sudo -u postgres psql <<EOF
-- Создание базы данных
CREATE DATABASE lab_db;

-- Переключение на базу данных
\c lab_db;

-- Создание схемы (опционально)
CREATE SCHEMA lab_schema;

-- Создание ролей (без права входа)
CREATE ROLE admin_role;
CREATE ROLE user_role;
CREATE ROLE guest_role;

-- Создание пользователей с правом входа
CREATE USER admin_user WITH PASSWORD 'admin_pass';
CREATE USER app_user WITH PASSWORD 'user_pass';
CREATE USER guest_user WITH PASSWORD 'guest_pass';

-- Назначение ролей пользователям
GRANT admin_role TO admin_user;
GRANT user_role TO app_user;
GRANT guest_role TO guest_user;

-- Настройка прав для ролей
-- Администратор: полный доступ ко всем объектам в схеме
GRANT ALL PRIVILEGES ON SCHEMA lab_schema TO admin_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA lab_schema TO admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA lab_schema TO admin_role;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA lab_schema TO admin_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA lab_schema GRANT ALL PRIVILEGES ON TABLES TO admin_role;

-- Пользователь: полный доступ к таблицам (CRUD)
GRANT USAGE ON SCHEMA lab_schema TO user_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA lab_schema TO user_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA lab_schema TO user_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA lab_schema GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO user_role;

-- Гость: только чтение
GRANT USAGE ON SCHEMA lab_schema TO guest_role;
GRANT SELECT ON ALL TABLES IN SCHEMA lab_schema TO guest_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA lab_schema GRANT SELECT ON TABLES TO guest_role;

-- Создание тестовой таблицы от имени администратора
SET ROLE admin_role;
CREATE TABLE lab_schema.test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    data TEXT
);
INSERT INTO lab_schema.test_table (name, data) VALUES ('Тест', 'Пример данных');
RESET ROLE;

-- Предоставление прав на созданную таблицу (повторно для надёжности)
GRANT ALL PRIVILEGES ON lab_schema.test_table TO admin_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON lab_schema.test_table TO user_role;
GRANT SELECT ON lab_schema.test_table TO guest_role;
GRANT USAGE, SELECT ON SEQUENCE lab_schema.test_table_id_seq TO user_role;
GRANT USAGE, SELECT ON SEQUENCE lab_schema.test_table_id_seq TO guest_role;

-- Вывод информации о ролях и правах
\du
\dp lab_schema.test_table

EOF

echo "Настройка PostgreSQL завершена."
