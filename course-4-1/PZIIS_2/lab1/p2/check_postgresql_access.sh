#!/bin/bash

# Проверка доступа для разных пользователей
check_user_access() {
    local user=$1
    local password=$2
    echo "=== Проверка для пользователя: $user ==="

    # Попытка SELECT (должна быть доступна всем)
    PGPASSWORD=$password psql -U $user -d lab_db -c "SELECT * FROM lab_schema.test_table;" 2>/dev/null && echo "  SELECT: ДА" || echo "  SELECT: НЕТ"

    # Попытка INSERT (должна быть доступна admin и user, но не guest)
    PGPASSWORD=$password psql -U $user -d lab_db -c "INSERT INTO lab_schema.test_table (name, data) VALUES ('$user', 'Тест');" 2>/dev/null && echo "  INSERT: ДА" || echo "  INSERT: НЕТ"

    # Попытка DELETE (должна быть доступна только admin)
    PGPASSWORD=$password psql -U $user -d lab_db -c "DELETE FROM lab_schema.test_table WHERE name='$user';" 2>/dev/null && echo "  DELETE: ДА" || echo "  DELETE: НЕТ"

    # Попытка создать таблицу (должна быть доступна только admin)
    PGPASSWORD=$password psql -U $user -d lab_db -c "CREATE TABLE lab_schema.test_$user (id int);" 2>/dev/null && echo "  CREATE TABLE: ДА" || echo "  CREATE TABLE: НЕТ"
}

# Проверка для каждого пользователя
check_user_access "admin_user" "admin_pass"
check_user_access "app_user" "user_pass"
check_user_access "guest_user" "guest_pass"
