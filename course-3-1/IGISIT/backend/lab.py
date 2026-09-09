import pandas as pd
import os
import io
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Устанавливаем стиль для графиков
sns.set_style('whitegrid')

# =====================================================
# 1. ДАННЫЕ ВРУЧНУЮ (ВВП)
# =====================================================
# Используем sep='\s+' в parse_gdp_manual для надежного парсинга
GDP_DATA_TEXT = """
год ВВП_млрд_долл ВВП_на_душу ВВП_мир_доля
1990 19.5 1868.0 0.085
1991 19.9 1899.0 0.082
1992 18.4 1752.0 0.071
1993 17.4 1657.0 0.066
1994 15.7 1496.0 0.056
1995 14.3 1369.0 0.046
1996 15.0 1436.0 0.047
1997 14.6 1401.0 0.046
1998 15.7 1519.0 0.050
1999 12.5 1217.0 0.038
2000 10.8 1050.0 0.032
2001 12.8 1252.0 0.038
2002 15.1 1489.0 0.043
2003 18.4 1831.0 0.047
2004 23.9 2393.0 0.054
2005 31.2 3144.0 0.065
2006 38.2 3870.0 0.074
2007 46.8 4764.0 0.080
2008 62.8 6417.0 0.098
2009 50.9 5214.0 0.084
2010 57.2 5881.0 0.086
2011 61.8 6363.0 0.083
2012 65.7 6776.0 0.087
2013 75.5 7793.0 0.097
2014 78.8 8130.0 0.099
2015 56.5 5820.0 0.075
2016 47.7 4916.0 0.062
2017 54.7 5637.0 0.067
2018 60.0 6192.0 0.069
2019 64.4 6658.0 0.073
2020 61.4 6370.0 0.072
2021 69.7 7274.0 0.072
2022 72.9 7643.0 0.072
"""

# =====================================================
# 1.1. ДАННЫЕ ВРУЧНУЮ (ИНФЛЯЦИЯ)
# =====================================================
INFLATION_DATA_TEXT = """
Год|Годовая инфляция (CPI, %)
1993|1190.2
1994|2221.0
1995|709.4
1996|52.7
1997|63.9
1998|72.9
1999|293.7
2000|168.6
2001|61.1
2002|42.5
2003|28.4
2004|18.1
2005|10.3
2006|7.0
2007|8.4
2008|14.8
2009|13.0
2010|7.7
2011|53.2
2012|59.2
2013|18.3
2014|18.1
2015|13.5
2016|11.8
2017|6.0
2018|4.9
2019|5.6
2020|5.6
2021|9.5
2022|15.21
2023|5.0
2024|5.8
"""

# --- Словари для нормализации ---
# Словарь: Русское имя файла -> Стандартизованный ключ (англ.)
INDICATOR_KEYS = {
    'Индекс_реальной_заработной_платы': 'Real_Wage_Index',
    'Номинальная_начисленная_среднемесячная_заработная_плата': 'Nominal_Monthly_Wage',
    'Среднесписочная_численность_работников': 'Average_Employee_Count',
    'Удельный_вес': 'Specific_Weight', # <-- Целевой ключ
    'Численность_безработных': 'Unemployed_Count',
    'Численность_занятого_населения_в_среднем_за_период': 'Employed_Count',
    'Численность_уволенных': 'Fired_Count',
    'Число_человеко_часов': 'Man_Hours',
    
    # Ключи для ручного ввода
    'ВВП_млрд_долл': 'GDP_Billion_USD',
    'ВВП_на_душу': 'GDP_Per_Capita',
    'ВВП_мир_доля': 'GDP_World_Share',
    'Годовая_инфляция_CPI': 'Inflation_CPI',
}

# Словарь: Стандартизованный ключ (англ.) -> Отображаемое имя (рус.)
DISPLAY_NAMES = {
    'Real_Wage_Index': 'Индекс реальной зарплаты',
    'Nominal_Monthly_Wage': 'Номинальная среднемес. зарплата',
    'Average_Employee_Count': 'Среднесписочная численность',
    'Specific_Weight': 'Удельный вес трудовых ресурсов',
    'Unemployed_Count': 'Численность безработных',
    'Employed_Count': 'Численность трудоустроенных',
    'Fired_Count': 'Численность уволенных',
    'Man_Hours': 'Число человеко-часов',
    'GDP_Billion_USD': 'ВВП, млрд USD',
    'GDP_Per_Capita': 'ВВП на душу населения',
    'GDP_World_Share': 'Доля ВВП в мировом',
    'Inflation_CPI': 'Годовая инфляция (CPI)'
}

def translate_indicator_name(name: str) -> str:
    """Преобразует русские имена файлов в стандартизированные ключи (англ)."""
    return INDICATOR_KEYS.get(name, name)

def get_display_name(key: str) -> str:
    """Возвращает русское имя для отображения."""
    # Используем DISPLAY_NAMES, а не старую translate_indicator_name
    return DISPLAY_NAMES.get(key, key)

# =====================================================
# 2. ФУНКЦИИ ОБРАБОТКИ
# =====================================================

def parse_gdp_manual() -> pd.DataFrame:
    """Парсит текстовые данные ВВП в DataFrame."""
    df = pd.read_csv(io.StringIO(GDP_DATA_TEXT), sep='\s+')
    df['region'] = 'Республика Беларусь'
    
    df_long = df.melt(
        id_vars=['год', 'region'],
        var_name='indicator',
        value_name='value'
    )
    df_long.rename(columns={'год': 'year'}, inplace=True)
    
    df_long['indicator'] = df_long['indicator'].apply(translate_indicator_name)
    return df_long

def parse_inflation_manual() -> pd.DataFrame:
    """Парсит текстовые данные инфляции в DataFrame."""
    df = pd.read_csv(io.StringIO(INFLATION_DATA_TEXT), sep='|')
    
    df.columns = ['year', 'value']
    
    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype(int)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['region'] = 'Республика Беларусь'
    
    df['indicator'] = translate_indicator_name('Годовая_инфляция_CPI')
    
    df = df[['year', 'region', 'indicator', 'value']]
    df.dropna(subset=['value'], inplace=True)
    
    return df

def process_belstat_csv(filepath: str) -> pd.DataFrame:
    """
    Умное чтение CSV от Белстата. Определяет заголовок и фильтрует по "Всего", 
    учитывая специфичную структуру и вносит корректировку для файлов безработицы и уд. веса.
    """
    filename = os.path.basename(filepath)
    indicator_name_ru = os.path.splitext(filename)[0]
    indicator_key = translate_indicator_name(indicator_name_ru)
    
    print(f"Обработка файла: {filename} ({indicator_key})...", end=" ")

    # 1. Определяем кодировку и строку заголовка
    encodings = ['utf-8', 'cp1251', 'windows-1251']
    header_index = 0
    lines = []
    
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                lines = f.readlines()
            
            # Находим строку с максимальным количеством разделителей (заголовки)
            semicolon_counts = [line.count(';') for line in lines[:10]]
            max_semicolons = max(semicolon_counts)
            header_index = semicolon_counts.index(max_semicolons)
            break
        except Exception:
            continue
            
    if not lines or max_semicolons < 1:
        print("ОШИБКА: Не удалось прочитать или найти разделитель ';'.")
        return pd.DataFrame()

    # 2. Парсинг данных
    try:
        data_content = "".join(lines[header_index:])
        df = pd.read_csv(io.StringIO(data_content), sep=';', dtype=str)
    except Exception as e:
        print(f"ОШИБКА парсинга: {e}")
        return pd.DataFrame()

    # 3. Нормализация заголовков и очистка
    df.columns = [str(c).strip() for c in df.columns]
    
    # Находим столбцы: регион, детализация, годы
    region_col = df.columns[0]
    
    # 4. Обработка столбцов в зависимости от структуры (содержит детализацию или нет)
    if len(df.columns) >= 7 and "Unnamed" not in df.columns[1]:
        # Предполагаем, что это специфичный/стандартный файл с двумя первыми столбцами: region и detail
        detail_col = df.columns[1]
        
        df.rename(columns={region_col: "region", detail_col: "detail"}, inplace=True)
        
        # Агрессивная очистка региона и детализации
        df["region"] = df["region"].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x).strip())
        df["detail"] = df["detail"].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x).strip())
        
        # *** КЛЮЧЕВАЯ ФИЛЬТРАЦИЯ ***
        
        if indicator_key == 'Unemployed_Count':
            # 🎯 СПЕЦИФИЧЕСКАЯ ФИЛЬТРАЦИЯ ДЛЯ БЕЗРАБОТИЦЫ
            target_detail = 'Всего зарегистрированной безработицы по продолжительности'
            df_filtered = df[
                df['detail'].str.contains(target_detail, case=False, na=False)
            ].copy()
            
            if df_filtered.empty:
                 print("ВНИМАНИЕ: Не найдена целевая строка 'Всего зарегистрированной...'. Использование широкой фильтрации.")
                 df_filtered = df[
                    (df['detail'].str.contains('Всего', case=False, na=False))
                 ].copy()
                 
        elif indicator_key == 'Employed_Count':
            # 🎯 СПЕЦИФИЧЕСКАЯ ФИЛЬТРАЦИЯ ДЛЯ УДЕЛЬНОГО ВЕСА ТРУДОВЫХ РЕСУРСОВ
            target_detail = 'Оба пола'
            df_filtered = df[
                df['detail'].str.contains(target_detail, case=False, na=False)
            ].copy()

            if df_filtered.empty:
                 print("ВНИМАНИЕ: Не найдена целевая строка 'Оба пола'. Использование широкой фильтрации.")
                 df_filtered = df[
                    (df['detail'].str.contains('Всего', case=False, na=False))
                 ].copy()
        elif indicator_key == 'Specific_Weight':
            target_detail = 'Всего по типам местности'
            df_filtered = df[
                df['detail'].str.contains(target_detail, case=False, na=False)
            ].copy()

            if df_filtered.empty:
                 print("ВНИМАНИЕ: Не найдена целевая строка 'Всего по типам местности'. Использование широкой фильтрации.")
                 df_filtered = df[
                    (df['detail'].str.contains('Всего', case=False, na=False))
                 ].copy()  
        else:
            # 🌐 УНИВЕРСАЛЬНАЯ ФИЛЬТРАЦИЯ ДЛЯ ОСТАЛЬНЫХ ФАЙЛОВ
            df_filtered = df[
                (df['detail'].str.contains('Всего', case=False, na=False)) | 
                (df['region'] == 'Республика Беларусь') | 
                (df['detail'].str.contains('Все', case=False, na=False))
            ].copy()
        
        # Удаляем столбец detail перед melt
        df_filtered = df_filtered.drop(columns=['detail'], errors='ignore')

        id_vars = ['region']
        
    else:
        # Предполагаем, что это более простой файл, где столбец "detail" отсутствует/объединен.
        df.rename(columns={region_col: "region"}, inplace=True)
        df["region"] = df["region"].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x).strip())
        df_filtered = df.copy()
        id_vars = ['region']
    
    # Определяем столбцы с годами
    year_cols = [c for c in df_filtered.columns if re.match(r'^\d{4}$', c)]
    
    if not year_cols:
        print("ОШИБКА: Не найдены столбцы с годами (YYYY).")
        return pd.DataFrame()

    # 5. Преобразование из широкого формата в длинный (melt)
    try:
        df_long = pd.melt(
            df_filtered,
            id_vars=id_vars,
            value_vars=year_cols,
            var_name="year",
            value_name="value"
        )
    except Exception as e:
        print(f"ОШИБКА melt: {e}")
        return pd.DataFrame()
    
    # 6. Финальная очистка и нормализация
    df_long["indicator"] = indicator_key
    
    # Заменяем запятую на точку, удаляем лишние пробелы и преобразуем в число
    df_long["value"] = df_long["value"].astype(str).str.replace(',', '.', regex=False)
    df_long["value"] = df_long["value"].str.replace(r'\s+', '', regex=True)
    
    df_long["year"] = pd.to_numeric(df_long["year"], errors='coerce')
    df_long["value"] = pd.to_numeric(df_long["value"], errors='coerce')
    
    df_long.dropna(subset=['year', 'value'], inplace=True)
    df_long["year"] = df_long["year"].astype(int)
    
    # Очистка региона после melt для надежности (если были Nan или мусор)
    df_long["region"] = df_long["region"].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x).strip())
    
    print(f"OK ({len(df_long)} строк)")
    return df_long[['year', 'region', 'indicator', 'value']]

def plot_trends(df: pd.DataFrame):
    """Строит ОТДЕЛЬНЫЙ график для каждого индикатора, используя русское имя для заголовка."""
    indicators = df["indicator"].unique()
    
    if len(indicators) == 0:
        print("Нет данных для отображения.")
        return

    print(f"\nПостроение {len(indicators)} графиков по отдельности...")

    for indicator in indicators:
        plt.figure(figsize=(12, 7)) 
        
        plot_data = df[df["indicator"] == indicator].copy().sort_values("year")
        
        # Получаем русское название для заголовка
        display_name = get_display_name(indicator) # Использование новой функции
        
        # Логарифмическая шкала для сильно меняющихся показателей (например, старая инфляция)
        is_inflation = 'inflation' in indicator.lower()
        if is_inflation and plot_data['value'].max() > 100:
             plt.yscale('log')
             y_label = "Значение (Логарифмическая шкала)"
        else:
             y_label = "Значение"

        sns.lineplot(
            data=plot_data,
            x="year",
            y="value",
            hue="region",
            marker="o",
            linewidth=2
        )
        
        plt.title(f"Динамика показателя: {display_name}", fontsize=16, pad=20)
        plt.xlabel("Год", fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0, title='Регион')
        
        plt.tight_layout()
        plt.show()

# =====================================================
# 3. ГЛАВНАЯ ФУНКЦИЯ
# =====================================================

def main():
    target_files = [
        "Индекс_реальной_заработной_платы.csv",
        "Номинальная_начисленная_среднемесячная_заработная_плата.csv",
        "Среднесписочная_численность_работников.csv",
        "Удельный_вес.csv",         # Добавлена адресная фильтрация
        "Численность_безработных.csv", 
        "Численность_занятого_населения_в_среднем_за_период.csv",
        "Численность_уволенных.csv",
        "Число_человеко_часов.csv"
    ]
    
    all_dfs = []
    current_dir = os.getcwd()
    print(f"Папка скрипта: {current_dir}\n")

    # 1. Читаем CSV (все файлы обрабатываются одной функцией)
    for filename in target_files:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            df = process_belstat_csv(filepath)
            if not df.empty:
                all_dfs.append(df)
        else:
            print(f"Файл не найден: {filename}")

    # 2. Читаем ВВП
    try:
        df_gdp = parse_gdp_manual()
        print(f"Данные ВВП (вручную): OK ({len(df_gdp)} строк)")
        all_dfs.append(df_gdp)
    except Exception as e:
        print(f"Ошибка ВВП: {e}")

    # 3. Читаем Инфляцию
    try:
        df_inflation = parse_inflation_manual()
        print(f"Данные Инфляции (вручную): OK ({len(df_inflation)} строк)")
        all_dfs.append(df_inflation)
    except Exception as e:
        print(f"Ошибка Инфляции: {e}")
        
    # 4. Объединяем
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        # Сортировка по стандартизованному имени
        final_df = final_df.sort_values(by=["indicator", "region", "year"])
        
        print("\n" + "="*80)
        print(f" ДАННЫЕ СОБРАНЫ. ВСЕГО ЗАПИСЕЙ: {len(final_df)}")
        print("="*80)
        
        # 5. Сохранение в файл CSV (используем путь, указанный пользователем)
        # Убедитесь, что этот путь существует!
        output_filename = "/home/kirillromanoff/University/ИТОГОВЫЙ_ДАТАСЕТ_РБ.csv"
        try:
            final_df.to_csv(output_filename, index=False, encoding='utf-8')
            print(f"✅ Результаты успешно сохранены в CSV: {output_filename}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении файла: {e}")

        # 6. Визуализация
        plot_trends(final_df)
    else:
        print("Нет данных для отображения.")

if __name__ == "__main__":
    main()