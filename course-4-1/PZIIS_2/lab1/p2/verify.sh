#!/bin/bash
# Часть 2: проверка политики доступа admin / app_user / guest.
# Запуск: ./verify.sh  (root не обязателен, нужен доступ к localhost:5432)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${SCRIPT_DIR}/results"
mkdir -p "${OUT_DIR}"
TSV="${OUT_DIR}/verify_acl.tsv"
TXT="${OUT_DIR}/verify_acl.txt"

DB="lab_db"
HOST="127.0.0.1"

: > "${TSV}"
: > "${TXT}"
printf 'user\toperation\tresult\texpected\tpass\n' >> "${TSV}"

yesno() { [[ $1 -eq 0 ]] && echo "ДА" || echo "НЕТ"; }

run_sql() {
  local user="$1" pass="$2" sql="$3"
  PGPASSWORD="${pass}" psql -h "${HOST}" -U "${user}" -d "${DB}" -v ON_ERROR_STOP=1 -c "${sql}" &>/dev/null
}

check_op() {
  local user="$1" pass="$2" op="$3" sql="$4" expected="$5"
  local rc result pass
  set +e
  run_sql "${user}" "${pass}" "${sql}"
  rc=$?
  set -e
  result="$(yesno "${rc}")"
  if [[ ${result} == "${expected}" ]]; then
    pass="OK"
  else
    pass="FAIL"
  fi
  printf '%s\t%s\t%s\t%s\t%s\n' "${user}" "${op}" "${result}" "${expected}" "${pass}" >> "${TSV}"
  printf '  %-14s результат=%-3s ожидалось=%-3s [%s]\n' "${op}" "${result}" "${expected}" "${pass}" | tee -a "${TXT}"
}

{
  echo "=== Проверка ACL PostgreSQL ==="
  echo "Дата: $(date -Is)"
  echo
} | tee -a "${TXT}"

# --- admin_user: полный доступ ---
echo "=== admin_user (ожидается полный доступ) ===" | tee -a "${TXT}"
check_op admin_user admin_pass SELECT \
  "SELECT * FROM lab_schema.test_table LIMIT 1;" "ДА"
check_op admin_user admin_pass INSERT \
  "INSERT INTO lab_schema.test_table (name, data) VALUES ('admin_ins', 'x');" "ДА"
check_op admin_user admin_pass UPDATE \
  "UPDATE lab_schema.test_table SET data='upd' WHERE name='admin_ins';" "ДА"
check_op admin_user admin_pass DELETE \
  "DELETE FROM lab_schema.test_table WHERE name='admin_ins';" "ДА"
check_op admin_user admin_pass CREATE_TABLE \
  "CREATE TABLE lab_schema.admin_tmp (id int);" "ДА"
check_op admin_user admin_pass DROP_TABLE \
  "DROP TABLE IF EXISTS lab_schema.admin_tmp;" "ДА"

# --- app_user: CRUD, без DDL ---
echo "=== app_user (CRUD, без DDL) ===" | tee -a "${TXT}"
check_op app_user user_pass SELECT \
  "SELECT * FROM lab_schema.test_table LIMIT 1;" "ДА"
check_op app_user user_pass INSERT \
  "INSERT INTO lab_schema.test_table (name, data) VALUES ('user_ins', 'x');" "ДА"
check_op app_user user_pass UPDATE \
  "UPDATE lab_schema.test_table SET data='upd' WHERE name='user_ins';" "ДА"
check_op app_user user_pass DELETE \
  "DELETE FROM lab_schema.test_table WHERE name='user_ins';" "ДА"
check_op app_user user_pass CREATE_TABLE \
  "CREATE TABLE lab_schema.user_tmp (id int);" "НЕТ"
check_op app_user user_pass DROP_TABLE \
  "DROP TABLE lab_schema.test_table;" "НЕТ"

# --- guest_user: только SELECT ---
echo "=== guest_user (только SELECT) ===" | tee -a "${TXT}"
check_op guest_user guest_pass SELECT \
  "SELECT * FROM lab_schema.test_table LIMIT 1;" "ДА"
check_op guest_user guest_pass INSERT \
  "INSERT INTO lab_schema.test_table (name, data) VALUES ('guest_ins', 'x');" "НЕТ"
check_op guest_user guest_pass UPDATE \
  "UPDATE lab_schema.test_table SET data='x' WHERE id=1;" "НЕТ"
check_op guest_user guest_pass DELETE \
  "DELETE FROM lab_schema.test_table WHERE id=1;" "НЕТ"
check_op guest_user guest_pass CREATE_TABLE \
  "CREATE TABLE lab_schema.guest_tmp (id int);" "НЕТ"

echo | tee -a "${TXT}"
fails="$(awk -F'\t' 'NR>1 && $5=="FAIL" {c++} END{print c+0}' "${TSV}")"
echo "Итого FAIL: ${fails}" | tee -a "${TXT}"
echo "Результаты: ${TXT}"
echo "Таблица TSV: ${TSV}"
[[ ${fails} -eq 0 ]]
