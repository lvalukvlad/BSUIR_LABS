#!/bin/bash

# Получаем путь к рабочему столу
desktop_path="$HOME/Рабочий стол"  # Для английской версии: "$HOME/Desktop"

# Имя файла
file_name="arguments.txt"

# Полный путь к файлу
file_path="$desktop_path/$file_name"

# Записываем аргументы в файл и выводим их на консоль
echo "Аргументы командной строки:" | tee "$file_path"
for arg in "$@"; do
    echo "$arg" | tee -a "$file_path"
done

echo "Аргументы записаны в файл '$file_path'."
