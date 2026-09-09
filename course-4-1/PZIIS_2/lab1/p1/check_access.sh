#!/bin/bash
# Скрипт проверки доступа check_access.sh

USERS=("iit11" "iit12" "iit21" "iit22" "iit3" "root")
DIRS=("/home/pzs/pzs11" "/home/pzs/pzs12" "/home/pzs/pzs13" "/home/pzs/pzs14" "/home/pzs/pzs15")

for user in "${USERS[@]}"; do
    echo "=== Проверка для пользователя: $user ==="
    for dir in "${DIRS[@]}"; do
        echo "Папка: $dir"
        # Проверка чтения содержимого
        sudo -u "$user" ls "$dir" 2>/dev/null && echo "  Чтение: ДА" || echo "  Чтение: НЕТ"
        # Проверка создания файла
        sudo -u "$user" touch "$dir/test_write" 2>/dev/null && echo "  Запись: ДА" || echo "  Запись: НЕТ"
        # Проверка удаления файла (на примере первого файла)
        first_file=$(sudo -u "$user" ls "$dir" | head -n1)
        if [ -n "$first_file" ]; then
            sudo -u "$user" rm "$dir/$first_file" 2>/dev/null && echo "  Удаление: ДА" || echo "  Удаление: НЕТ"
        fi
    done
done
