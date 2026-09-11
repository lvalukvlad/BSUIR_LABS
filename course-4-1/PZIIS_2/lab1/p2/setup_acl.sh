#!/bin/bash
# Часть 2: роли admin / user / guest и объекты БД.
# Запуск: sudo ./setup_acl.sh
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Ошибка: запускайте от root (sudo ./setup_acl.sh)" >&2
  exit 1
fi

DB_NAME="lab_db"
SCHEMA="lab_schema"

echo "==> Настройка pg_hba.conf (пароль только для учёток лабы)"
PG_HBA="$(sudo -u postgres psql -tA -c "SHOW hba_file;" | tr -d '[:space:]')"

if [[ -n ${PG_HBA} && -f ${PG_HBA} ]]; then
  if [[ ! -f ${PG_HBA}.lab1.bak ]]; then
    cp -a "${PG_HBA}" "${PG_HBA}.lab1.bak"
  fi
  # Удаляем прошлые правила лабы, затем добавляем точечные
  grep -vE 'lab_db.*(admin_user|app_user|guest_user|LAB1)' "${PG_HBA}" > "${PG_HBA}.tmp" || cp -a "${PG_HBA}" "${PG_HBA}.tmp"
  {
    echo "# LAB1: password auth for lab accounts only"
    echo "local   lab_db   admin_user,app_user,guest_user                     scram-sha-256"
    echo "host    lab_db   admin_user,app_user,guest_user   127.0.0.1/32      scram-sha-256"
    echo "host    lab_db   admin_user,app_user,guest_user   ::1/128           scram-sha-256"
    cat "${PG_HBA}.tmp"
  } > "${PG_HBA}"
  rm -f "${PG_HBA}.tmp"
fi

sudo -u postgres psql -c "ALTER SYSTEM SET password_encryption = 'scram-sha-256';" 2>/dev/null || true

if command -v systemctl &>/dev/null && systemctl is-active --quiet postgresql 2>/dev/null; then
  systemctl reload postgresql || systemctl restart postgresql
elif command -v pg_lsclusters &>/dev/null; then
  service postgresql reload 2>/dev/null || service postgresql restart 2>/dev/null || true
else
  service postgresql reload || service postgresql restart || true
fi

echo "==> Пересоздание БД и ролей"
sudo -u postgres psql <<EOF
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ${DB_NAME};
DROP ROLE IF EXISTS admin_user;
DROP ROLE IF EXISTS app_user;
DROP ROLE IF EXISTS guest_user;
DROP ROLE IF EXISTS admin_role;
DROP ROLE IF EXISTS user_role;
DROP ROLE IF EXISTS guest_role;

CREATE DATABASE ${DB_NAME};

CREATE ROLE admin_role NOLOGIN;
CREATE ROLE user_role  NOLOGIN;
CREATE ROLE guest_role NOLOGIN;

CREATE ROLE admin_user LOGIN PASSWORD 'admin_pass';
CREATE ROLE app_user   LOGIN PASSWORD 'user_pass';
CREATE ROLE guest_user LOGIN PASSWORD 'guest_pass';

GRANT admin_role TO admin_user;
GRANT user_role  TO app_user;
GRANT guest_role TO guest_user;

GRANT CONNECT ON DATABASE ${DB_NAME} TO admin_role, user_role, guest_role;
EOF

echo "==> Схема, таблица и GRANT"
sudo -u postgres psql -d "${DB_NAME}" <<EOF
CREATE SCHEMA ${SCHEMA};

GRANT USAGE ON SCHEMA ${SCHEMA} TO admin_role, user_role, guest_role;
GRANT ALL PRIVILEGES ON SCHEMA ${SCHEMA} TO admin_role;
GRANT CREATE ON SCHEMA ${SCHEMA} TO admin_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA ${SCHEMA}
  GRANT ALL PRIVILEGES ON TABLES TO admin_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA ${SCHEMA}
  GRANT ALL PRIVILEGES ON SEQUENCES TO admin_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA ${SCHEMA}
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO user_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA ${SCHEMA}
  GRANT USAGE, SELECT ON SEQUENCES TO user_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA ${SCHEMA}
  GRANT SELECT ON TABLES TO guest_role;

CREATE TABLE ${SCHEMA}.test_table (
  id   SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  data TEXT
);

INSERT INTO ${SCHEMA}.test_table (name, data) VALUES ('seed', 'initial row');

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ${SCHEMA} TO admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ${SCHEMA} TO admin_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ${SCHEMA} TO user_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ${SCHEMA} TO user_role;
GRANT SELECT ON ALL TABLES IN SCHEMA ${SCHEMA} TO guest_role;

\du
\dp ${SCHEMA}.test_table
EOF

echo "==> Проверка входа admin_user"
if ! PGPASSWORD=admin_pass psql -h 127.0.0.1 -U admin_user -d "${DB_NAME}" -c "SELECT 1 AS ok;"; then
  echo "==> Fallback: md5 в pg_hba для учёток лабы"
  if [[ -n ${PG_HBA} && -f ${PG_HBA} ]]; then
    sed -i 's/scram-sha-256/md5/g' "${PG_HBA}"
    service postgresql reload 2>/dev/null || systemctl reload postgresql 2>/dev/null || true
  fi
  PGPASSWORD=admin_pass psql -h 127.0.0.1 -U admin_user -d "${DB_NAME}" -c "SELECT 1 AS ok;"
fi

echo "Настройка завершена. Дальше: ./verify.sh"
