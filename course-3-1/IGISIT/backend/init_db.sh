#!/bin/bash
set -e

echo "Ожидание запуска PostgreSQL..."
sleep 5

echo "Запуск db.py для создания таблиц..."
python db.py

echo "Запуск load_data.py для загрузки данных..."
python load_data.py

echo "Запуск predict_model.py для прогнозирования..."
python predict_model.py

echo "Инициализация базы данных завершена!"