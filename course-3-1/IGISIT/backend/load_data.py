# load_data.py

import pandas as pd
from sqlalchemy.orm import Session
from db import IndicatorData, engine, init_db
import os


# Вариант 2: Через os.path для надежности
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "ИТОГОВЫЙ_ДАТАСЕТ_РБ.csv")
TABLE_NAME = IndicatorData.__tablename__

# --- 2. Словарь для перевода метрик на русский (с пробелами) ---
METRICS_TRANSLATION = {
    "Employed_Count": "Численность занятых(в тыс.)",
    "Specific_Weight": "Удельный вес",
    "GDP_World_Share": "Доля в мировом ВВП",
    "Nominal_Monthly_Wage": "Номинальная месячная зарплата",
    "Average_Employee_Count": "Среднесписочная численность",
    "Real_Wage_Index": "Индекс реальной заработной платы",
    "GDP_Per_Capita": "ВВП на душу населения",
    "GDP_Billion_USD": "ВВП млрд долл США",
    "Inflation_CPI": "Инфляция ИПЦ",
    "Fired_Count": "Число уволенных",
    "Unemployed_Count": "Число безработных",
    "Man_Hours": "Отработанные человеко-часы"
}

def load_data_to_db():
    """Считывает CSV, обрабатывает данные (перевод метрик, очистка регионов) и загружает их в базу данных."""
    try:
        # 1. Проверяем наличие файла
        if not os.path.exists(CSV_PATH):
            print(f"ОШИБКА: Файл не найден по пути: {CSV_PATH}")
            return

        # 2. Чтение данных
        print(f"Чтение данных из: {CSV_PATH}...")
        # Используем дефолтный разделитель pandas, как в рабочем варианте
        df = pd.read_csv(CSV_PATH, encoding='utf-8') 
        
        # --- 3. Предварительная обработка данных ---
        
        # a) Очистка названий регионов от лишних пробелов в начале и конце
        print("Очистка названий регионов от пробелов...")
        # Применяем .str.strip() для удаления пробелов с начала и конца строки
        df['region'] = df['region'].astype(str).str.strip()
        
        # b) Перевод названий метрик на русский
        print("Перевод названий метрик на русский язык...")
        # Применяем словарь-переводчик к столбцу indicator
        df['indicator'] = df['indicator'].replace(METRICS_TRANSLATION)
        
        # c) Убедимся, что столбцы соответствуют модели:
        # Эту строку оставляем, так как она работала и гарантирует нужный порядок для БД
        df = df[['year', 'region', 'indicator', 'value']]
        df = df.dropna(subset=['value'])
        
        # 4. Создание таблиц (на случай, если не было сделано ранее)
        init_db() # Гарантируем, что таблицы существуют

        # 5. Загрузка данных в базу
        print(f"Загрузка {len(df)} обработанных записей в таблицу '{TABLE_NAME}'...")
        
        # Используем 'append' для записи в существующую схему
        df.to_sql(TABLE_NAME, con=engine, if_exists='append', index=False) 
    
        
        print("✅ Загрузка данных завершена успешно. Регионы очищены, метрики переведены.")

    except Exception as e:
        print(f"❌ Произошла ошибка при загрузке данных: {e}")

if __name__ == '__main__':
    load_data_to_db()