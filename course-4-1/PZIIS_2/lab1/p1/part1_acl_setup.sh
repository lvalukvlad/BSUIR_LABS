#!/bin/bash

# Скрипт необходимо запускать с правами root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root" 
   exit 1
fi

# --- 1. Создание групп ---
echo "Создание групп..."
groupadd group_iit1 2>/dev/null
groupadd group_iit2 2>/dev/null

# --- 2-4. Создание пользователей и добавление в группы ---
echo "Создание пользователей..."
useradd -m -G group_iit1 iit11
useradd -m -G group_iit1 iit12
useradd -m -G group_iit2 iit21
useradd -m -G group_iit2 iit22
useradd -m iit3

# --- 4. Предоставление административных привилегий пользователю iit21 ---
echo "Предоставление административных привилегий iit21..."
usermod -aG sudo iit21

# --- 5-6. Создание базовой папки и папок с разными владельцами ---
echo "Создание папок..."
mkdir -p /home/pzs
mkdir /home/pzs/pzs11
mkdir /home/pzs/pzs12
mkdir /home/pzs/pzs13
mkdir /home/pzs/pzs14
mkdir /home/pzs/pzs15

# --- 7-11. Настройка прав доступа для папок с помощью chmod ---
# Владелец (700)
chmod 700 /home/pzs/pzs11
# Группа (070)
chmod 070 /home/pzs/pzs12
# Остальные (007)
chmod 007 /home/pzs/pzs13
# Все (777)
chmod 777 /home/pzs/pzs14
# Администратор (root) - оставляем 700, владелец root
chmod 700 /home/pzs/pzs15
chown root:root /home/pzs/pzs15

# --- 12. Смена текущего пользователя на iit11 для создания файлов ---
# Создаём функции для создания файлов от имени iit11
create_files_as_iit11() {
    local base_dir=$1
    # file11 - только чтение для владельца (400)
    touch "$base_dir/file11" && chmod 400 "$base_dir/file11"
    # file12 - чтение и запись для владельца (600)
    touch "$base_dir/file12" && chmod 600 "$base_dir/file12"
    # file13 - только запись для владельца (200)
    touch "$base_dir/file13" && chmod 200 "$base_dir/file13"
    # file14 - чтение, запись, выполнение для владельца (700)
    touch "$base_dir/file14" && chmod 700 "$base_dir/file14"
    # file15 - только выполнение для владельца (100)
    touch "$base_dir/file15" && chmod 100 "$base_dir/file15"

    # file21 - только чтение для группы group_iit1 (040)
    touch "$base_dir/file21" && chmod 040 "$base_dir/file21"
    chown :group_iit1 "$base_dir/file21"
    # file22 - чтение и запись для группы (060)
    touch "$base_dir/file22" && chmod 060 "$base_dir/file22"
    chown :group_iit1 "$base_dir/file22"
    # file23 - только запись для группы (020)
    touch "$base_dir/file23" && chmod 020 "$base_dir/file23"
    chown :group_iit1 "$base_dir/file23"
    # file24 - чтение, запись, выполнение для группы (070)
    touch "$base_dir/file24" && chmod 070 "$base_dir/file24"
    chown :group_iit1 "$base_dir/file24"
    # file25 - только выполнение для группы (010)
    touch "$base_dir/file25" && chmod 010 "$base_dir/file25"
    chown :group_iit1 "$base_dir/file25"

    # file31 - только чтение для остальных (004)
    touch "$base_dir/file31" && chmod 004 "$base_dir/file31"
    # file32 - чтение и запись для остальных (006)
    touch "$base_dir/file32" && chmod 006 "$base_dir/file32"
    # file33 - только запись для остальных (002)
    touch "$base_dir/file33" && chmod 002 "$base_dir/file33"
    # file34 - чтение, запись, выполнение для остальных (007)
    touch "$base_dir/file34" && chmod 007 "$base_dir/file34"
    # file35 - только выполнение для остальных (001)
    touch "$base_dir/file35" && chmod 001 "$base_dir/file35"

    # file41 - только чтение для всех (444)
    touch "$base_dir/file41" && chmod 444 "$base_dir/file41"
    # file42 - чтение и запись для всех (666)
    touch "$base_dir/file42" && chmod 666 "$base_dir/file42"
    # file43 - только запись для всех (222)
    touch "$base_dir/file43" && chmod 222 "$base_dir/file43"
    # file44 - чтение, запись, выполнение для всех (777)
    touch "$base_dir/file44" && chmod 777 "$base_dir/file44"
    # file45 - только выполнение для всех (111)
    touch "$base_dir/file45" && chmod 111 "$base_dir/file45"

    # file51 - только чтение для администратора (400, владелец root)
    touch "$base_dir/file51" && chmod 400 "$base_dir/file51" && chown root:root "$base_dir/file51"
    # file52 - чтение и запись для администратора (600)
    touch "$base_dir/file52" && chmod 600 "$base_dir/file52" && chown root:root "$base_dir/file52"
    # file53 - только запись для администратора (200)
    touch "$base_dir/file53" && chmod 200 "$base_dir/file53" && chown root:root "$base_dir/file53"
    # file54 - чтение, запись, выполнение для администратора (700)
    touch "$base_dir/file54" && chmod 700 "$base_dir/file54" && chown root:root "$base_dir/file54"
    # file55 - только выполнение для администратора (100)
    touch "$base_dir/file55" && chmod 100 "$base_dir/file55" && chown root:root "$base_dir/file55"

    # --- Заполнение файлов содержимым ---
    # Файлы, удовлетворяющие шаблону «flex5»: file51, file52, file53, file54, file55
    for f in file51 file52 file53 file54 file55; do
        echo "read testVariable" > "$base_dir/$f"
    done
    # Остальные файлы
    for f in file11 file12 file13 file14 file15 file21 file22 file23 file24 file25 \
             file31 file32 file33 file34 file35 file41 file42 file43 file44 file45; do
        echo "echo \"Hello World\"" > "$base_dir/$f"
    done
}

# Переключаемся на пользователя iit11 и создаём файлы
echo "Создание файлов от имени iit11..."
su - iit11 -c "bash -c '$(declare -f create_files_as_iit11); create_files_as_iit11 /home/pzs/pzs11'"
su - iit11 -c "bash -c '$(declare -f create_files_as_iit11); create_files_as_iit11 /home/pzs/pzs12'"
su - iit11 -c "bash -c '$(declare -f create_files_as_iit11); create_files_as_iit11 /home/pzs/pzs13'"
su - iit11 -c "bash -c '$(declare -f create_files_as_iit11); create_files_as_iit11 /home/pzs/pzs14'"

# Папка pzs15 принадлежит root, поэтому файлы создаём от имени root
echo "Создание файлов в pzs15 от имени root..."
create_files_as_iit11 /home/pzs/pzs15
chown -R root:root /home/pzs/pzs15

echo "Часть 1 завершена. Файлы и папки созданы."

# --- 17. Удаление созданных файлов, папок, пользователей и групп ---
# Этот блок можно раскомментировать для автоматической очистки после проверки
: <<'END_COMMENT'
echo "Очистка системы..."
rm -rf /home/pzs
userdel -r iit11
userdel -r iit12
userdel -r iit21
userdel -r iit22
userdel -r iit3
groupdel group_iit1
groupdel group_iit2
echo "Очистка завершена."
END_COMMENT
