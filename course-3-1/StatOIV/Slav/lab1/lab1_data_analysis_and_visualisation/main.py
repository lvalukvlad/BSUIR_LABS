import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

# Настройка стиля
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12

'''Предобработка данных. Загрузка данных'''
# Загрузка датасета
print("Загрузка данных...")
df = pd.read_csv('crocodile_dataset.csv')

'''Предобработка данных. Первичный анализ структуры данных'''
# Основная информация о датасете
print("\nПервые 5 строк датасета:")
print(df.head())

print("\nИнформация о датасете (info):")
print(df.info())

print("\nКраткая статистика (describe):")
print(df.describe(include='all'))

# Проверка размерности
print(f"\nРазмер датасета: {df.shape}")
print("\nТипы данных:")
print(df.dtypes)

'''Предобработка данных. Обработка пропущенных значений'''
print("\nОбработка пропусков.")
print("Количество пропусков по столбцам:")
print(df.isnull().sum())
print("\nПроцент пропусков:")
print((df.isnull().sum() / len(df) * 100).round(2))

# Для численных столбцов: заполним медианой (как в заготовке)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"\nЧисловые столбцы для заполнения медианой: {numeric_cols}")
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

# Для категориальных: заполним наиболее частыми значениями
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
# Исключим 'Notes' и 'Observer Name' — можно оставить NaN или заполнить 'Unknown'
for col in categorical_cols:
    if df[col].isnull().sum() > 0:
        mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown'
        df[col] = df[col].fillna(mode_val)

# Проверка пропусков после обработки
print("\nПропуски после первичной обработки:")
print(df.isnull().sum())

'''Предобработка данных. Обработка дубликатов'''
# Поиск и удаление дубликатов
print(f"\nКоличество дубликатов: {df.duplicated().sum()}")
df = df.drop_duplicates()
print(f"Дубликатов после удаления: {df.duplicated().sum()}")
print(f"Новый размер датасета: {df.shape}")

'''Предобработка данных. Обработка выбросов'''
# Метод межквартильного размаха (IQR)
# Обработка выбросов (IQR для 'Price')
print("\nАнализ выбросов (IQR) для ключевых числовых столбцов.")
# Используем только основные численные признаки: Length, Weight
num_for_outliers = []
if 'Observed Length (m)' in df.columns:
    num_for_outliers.append('Observed Length (m)')
if 'Observed Weight (kg)' in df.columns:
    num_for_outliers.append('Observed Weight (kg)')

for col in num_for_outliers:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)][col]
    print(f"\nСтолбец: {col}")
    print(f"Q1={Q1:.3f}, Q3={Q3:.3f}, IQR={IQR:.3f}")
    print(f"Нижняя граница: {lower:.3f}, Верхняя граница: {upper:.3f}")
    print(f"Количество выбросов: {len(outliers)}")
    if not outliers.empty:
        print("Примеры выбросов:", outliers.head().tolist())

# Можно удалить выбросы:
# df = df[(df['Observed Length (m)'] >= lower_length) & (df['Observed Length (m)'] <= upper_length)]

'''Предобработка данных. Преобразование типов данных'''
print("\nПреобразование типов данных")
# Дата по формату '%d-%m-%Y'
if 'Date of Observation' in df.columns:
    try:
        df['Date of Observation'] = pd.to_datetime(df['Date of Observation'], format='%d-%m-%Y')
    except Exception as e:
        # Если формат разные, попробуем общий парсинг
        print("Предупреждение: явное преобразование дат не прошло. Попытка общего парсинга...")
        df['Date of Observation'] = pd.to_datetime(df['Date of Observation'], errors='coerce')

    # Вытащим год и месяц
    df['Observation Year'] = df['Date of Observation'].dt.year
    df['Observation Month'] = df['Date of Observation'].dt.month
    print("Преобразованы даты. Примеры:")
    print(df[['Date of Observation', 'Observation Year', 'Observation Month']].head())

# Числовые: принудительно к числам
for col in ['Observed Length (m)', 'Observed Weight (kg)']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Категории
cat_cols = ['Common Name','Scientific Name','Family','Genus','Age Class','Sex',
            'Country/Region','Habitat Type','Conservation Status','Observer Name']
for c in cat_cols:
    if c in df.columns:
        df[c] = df[c].astype('category')

print("\nТипы данных после преобразования:")
print(df.dtypes)

'''Создание новых признаков'''
print("\nСоздание производных признаков.")
# Отношение веса к длине (условный индекс "плотности" особи)
if all(col in df.columns for col in ['Observed Weight (kg)', 'Observed Length (m)']):
    df['Weight_per_m'] = df['Observed Weight (kg)'] / df['Observed Length (m)'].replace({0: np.nan})
    print("Создан признак 'Weight_per_m'")

# Флаг крупной особи (например, длина > 4 м - условно)
if 'Observed Length (m)' in df.columns:
    # выберем порог как 90-й перцентиль или фиксированный 4.0, что меньше
    length_90 = df['Observed Length (m)'].quantile(0.90)
    threshold = min(4.0, length_90) if not np.isnan(length_90) else 4.0
    df['Is_Large'] = (df['Observed Length (m)'] >= threshold).astype(int)
    print(f"Флаг 'Is_Large' создан с порогом {threshold:.2f} м (90-й перцентиль = {length_90:.2f})")

# Сезон — для анализа сезонности
if 'Observation Month' in df.columns:
    def month_to_season(m):
        if pd.isna(m): 
            return np.nan
        m = int(m)
        if m in [12,1,2]:
            return 'Winter'
        elif m in [3,4,5]:
            return 'Spring'
        elif m in [6,7,8]:
            return 'Summer'
        else:
            return 'Autumn'
    df['Season'] = df['Observation Month'].apply(month_to_season).astype('category')
    print("Добавлен признак 'Season' (Winter/Spring/Summer/Autumn)")

'''Сохранение очищенного датасета'''
cleaned_path = 'cleaned_crocodile_dataset.csv'
df.to_csv(cleaned_path, index=False)
print(f"\nЧистый датасет: {cleaned_path}")

'''Анализ данных. Описательная статистика'''
print("\nОписательная статистика.")
print(df.describe(include='all').T)

# Дополнительные меры для ключевых числовых столбцов
columns_to_analyze = []
if 'Observed Length (m)' in df.columns:
    columns_to_analyze.append('Observed Length (m)')
if 'Observed Weight (kg)' in df.columns:
    columns_to_analyze.append('Observed Weight (kg)')
if 'Weight_per_m' in df.columns:
    columns_to_analyze.append('Weight_per_m')

for col in columns_to_analyze:
    series = df[col].dropna()
    median = series.median()
    mode = series.mode().iloc[0] if not series.mode().empty else np.nan
    var = series.var()
    std = series.std()
    skewness = series.skew()
    kurt = series.kurtosis()
    print(f"\nСтатистика для {col}:")
    print(f"Медиана: {median:.3f}")
    print(f"Мода: {mode}")
    print(f"Дисперсия: {var:.3f}")
    print(f"Стандартное отклонение: {std:.3f}")
    print(f"Скос: {skewness:.3f}")
    print(f"Куртозис: {kurt:.3f}")
    # Интерпретация
    if skewness > 0:
        print("Интерпретация: распределение смещено вправо — много мелких особей и несколько очень больших.")
    elif skewness < 0:
        print("Интерпретация: распределение смещено влево.")
    else:
        print("Интерпретация: распределение симметрично.")
    if kurt > 0:
        print("Куртозис положительный — тяжёлые хвосты/ярко выраженный пик.")
    elif kurt < 0:
        print("Куртозис отрицательный — более плоское распределение.")
    else:
        print("Куртозис близок к нулю.")

'''Анализ данных. Корреляционный анализ'''
print("\nКорреляционный анализ.")
# Формируем таблицу только с числовыми колонками, у которых мало NaN
num_df = df.select_dtypes(include=[np.number]).copy()
num_df = num_df.dropna(axis=1, how='all')
corr_matrix = num_df.corr()
print("\nМатрица корреляций (числовые признаки):")
print(corr_matrix)

# Тепловая карта корреляций
plt.figure(figsize=(12,8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f', cbar_kws={'label':'Correlation'})
plt.title('Матрица корреляций (числовые признаки)')
plt.tight_layout()
plt.show()

# Пары: Length vs Weight
if ('Observed Length (m)' in num_df.columns) and ('Observed Weight (kg)' in num_df.columns):
    corr_val = num_df['Observed Length (m)'].corr(num_df['Observed Weight (kg)'])
    print(f"\nКорреляция между длиной и весом: {corr_val:.3f}")
    # Тест Пирсона (убираем NaN)
    clean_pair = num_df[['Observed Length (m)', 'Observed Weight (kg)']].dropna()
    if len(clean_pair) > 2:
        corr_coef, p_value = pearsonr(clean_pair['Observed Length (m)'], clean_pair['Observed Weight (kg)'])
        print(f"Pearson r = {corr_coef:.3f}, p-value = {p_value:.4f}")
        if p_value < 0.05:
            print("Корреляция статистически значима (p < 0.05).")
        else:
            print("Корреляция не является статистически значимой (p >= 0.05).")

'''Анализ данных. Группировка и агрегация'''
print("\nГруппировки и агрегации.")
if 'Common Name' in df.columns:
    grouped_common = df.groupby('Common Name', observed=True)
    group_stats = grouped_common.agg({
        'Observed Length (m)': ['mean', 'median', 'min', 'max', 'std', 'count'],
        'Observed Weight (kg)': ['mean', 'median', 'min', 'max', 'std']
    })
    print("\nСтатистика по Common Name (первые 10):")
    print(group_stats.head(10))

# Сводная таблица: средняя длина по стране и по возрастной группе
if all(col in df.columns for col in ['Country/Region', 'Age Class', 'Observed Length (m)']):
    pivot_table = df.pivot_table(values='Observed Length (m)', index='Country/Region', columns='Age Class', aggfunc='mean', fill_value=np.nan, observed=True)
    print("\nСводная таблица: средняя длина по странам и возрастным классам (обрезано):")
    print(pivot_table.head(10))

'''Анализ данных. Временные ряды'''
print("\nВременные ряды и тренды.")
if 'Date of Observation' in df.columns:
    df_time = df.set_index('Date of Observation').sort_index()
    # Ресемплинг по году — средние значения длины/веса
    numeric_cols_for_resample = [c for c in ['Observed Length (m)', 'Observed Weight (kg)'] if c in df_time.columns]
    if numeric_cols_for_resample:
        yearly = df_time[numeric_cols_for_resample].resample('YE').mean()
        print("\nСредние по годам (последние 10):")
        print(yearly.tail(10))
        # Визуализация
        plt.figure(figsize=(10,6))
        for c in numeric_cols_for_resample:
            plt.plot(yearly.index.year, yearly[c], marker='o', label=c)
        plt.title('Средние показатели по годам')
        plt.xlabel('Год')
        plt.ylabel('Значение')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Скользящее среднее по длине (окно 3 года)
if 'Observed Length (m)' in df.columns:
    df = df.sort_values(by='Date of Observation') if 'Date of Observation' in df.columns else df
    df['rolling_length_3'] = df['Observed Length (m)'].rolling(window=3, min_periods=1).mean()
    print("\nПримеры скользящих средних длины (первые 5):")
    print(df[['Observed Length (m)', 'rolling_length_3']].head())


'''Визуализация данных. Одномерная визуализация. Количественные признаки. Гистограммы и графики плотности'''
print("\nВизуализации: одномерные.")
# Гистограммы для длины и веса
if 'Observed Length (m)' in df.columns:
    plt.figure(figsize=(10,6))
    plt.hist(df['Observed Length (m)'].dropna(), bins=30, alpha=0.7, edgecolor='black')
    plt.title('Распределение наблюдаемой длины (м)')
    plt.xlabel('Observed Length (m)')
    plt.ylabel('Частота')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if 'Observed Weight (kg)' in df.columns:
    plt.figure(figsize=(10,6))
    sns.histplot(data=df, x='Observed Weight (kg)', kde=True, bins=30)
    plt.title('Распределение наблюдаемого веса (кг) с KDE')
    plt.tight_layout()
    plt.show()

'''Визуализация данных. Одномерная визуализация. Количественные признаки. Box plot. Violin plot'''
# Boxplot и violin
if 'Observed Length (m)' in df.columns:
    plt.figure(figsize=(8,6))
    sns.boxplot(y=df['Observed Length (m)'])
    plt.title('Boxplot: Observed Length (m)')
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8,6))
    sns.violinplot(y=df['Observed Length (m)'])
    plt.title('Violin plot: Observed Length (m)')
    plt.tight_layout()
    plt.show()

'''Визуализация данных. Одномерная визуализация. Количественные признаки. Countplot'''
print("\nВизуализации: категориальные признаки.")
if 'Common Name' in df.columns:
    plt.figure(figsize=(12,6))
    df['Common Name'].value_counts().head(20).plot(kind='bar')
    plt.title('Топ-20 видов по числу наблюдений (Common Name)')
    plt.xlabel('Common Name')
    plt.ylabel('Количество наблюдений')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if 'Country/Region' in df.columns:
    plt.figure(figsize=(12,6))
    df['Country/Region'].value_counts().head(20).plot(kind='bar')
    plt.title('Топ-20 стран/регионов по числу наблюдений')
    plt.xlabel('Country/Region')
    plt.ylabel('Количество')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Countplot с hue по возрастному классу
if all(col in df.columns for col in ['Country/Region', 'Age Class']):
    plt.figure(figsize=(12,6))
    sns.countplot(data=df, x='Country/Region', hue='Age Class', order=df['Country/Region'].value_counts().index[:10])
    plt.title('Распределение возрастных классов по топ-10 стран')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Визуализация данных. Многомерные(scatter, regplot, pairplot)
print("\nВизуализации: многомерные.")
# Scatter Length vs Weight
if all(col in df.columns for col in ['Observed Length (m)', 'Observed Weight (kg)']):
    plt.figure(figsize=(10,6))
    plt.scatter(df['Observed Length (m)'], df['Observed Weight (kg)'], alpha=0.6)
    plt.xlabel('Observed Length (m)')
    plt.ylabel('Observed Weight (kg)')
    plt.title('Длина vs Вес')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10,6))
    sns.regplot(data=df, x='Observed Length (m)', y='Observed Weight (kg)', scatter_kws={'alpha':0.6})
    plt.title('Длина vs Вес с линией тренда')
    plt.tight_layout()
    plt.show()

# Scatter с цветом по возрастному классу
if all(col in df.columns for col in ['Observed Length (m)', 'Observed Weight (kg)', 'Age Class']):
    plt.figure(figsize=(10,6))
    sns.scatterplot(data=df, x='Observed Length (m)', y='Observed Weight (kg)', hue='Age Class', alpha=0.7)
    plt.title('Длина vs Вес по возрастным классам')
    plt.tight_layout()
    plt.show()

# Pairplot для ключевых чисел
pair_cols = [c for c in ['Observed Length (m)', 'Observed Weight (kg)', 'Weight_per_m'] if c in df.columns]
if pair_cols and len(pair_cols) >= 2:
    sns.pairplot(df[pair_cols].dropna(), diag_kind='hist')
    plt.suptitle('Pairplot для ключевых числовых признаков', y=1.02)
    plt.tight_layout()
    plt.show()

# Pairplot с hue по Common Name (если не слишком много уникальных)
if 'Common Name' in df.columns and len(df['Common Name'].cat.categories) <= 8:
    sns.pairplot(df, vars=pair_cols, hue='Common Name')
    plt.suptitle('Pairplot по видам', y=1.02)
    plt.tight_layout()
    plt.show()

'''Визуализация данных. Количественные против категориальных(box/violin по группам)'''
print("\nВизуализация количественных по группам.")
if all(col in df.columns for col in ['Common Name', 'Observed Length (m)']):
    plt.figure(figsize=(14,6))
    sns.boxplot(data=df, x='Common Name', y='Observed Length (m)')
    plt.title('Длина по видам (boxplot)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if all(col in df.columns for col in ['Habitat Type', 'Observed Weight (kg)']):
    plt.figure(figsize=(14,6))
    sns.violinplot(data=df, x='Habitat Type', y='Observed Weight (kg)')
    plt.title('Вес по типам среды обитания (violin)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

"""Визуализация данных. Таблица сопряжённости"""
print("\nТаблицы сопряженности.")
if all(col in df.columns for col in ['Age Class', 'Sex']):
    contingency = pd.crosstab(df['Age Class'], df['Sex'])
    print("Таблица сопряженности Age Class x Sex:")
    print(contingency)
    plt.figure(figsize=(8,6))
    sns.heatmap(contingency, annot=True, fmt='d', cmap='Blues')
    plt.title('Age Class vs Sex')
    plt.tight_layout()
    plt.show()

# Процентная таблица Age Class vs Habitat Type
if all(col in df.columns for col in ['Age Class', 'Habitat Type']):
    contingency_pct = pd.crosstab(df['Age Class'], df['Habitat Type'], normalize='index') * 100
    print("\nПроцентная таблица Age Class x Habitat Type:")
    print(contingency_pct.round(1))
    plt.figure(figsize=(10,6))
    sns.heatmap(contingency_pct, annot=True, fmt='.1f', cmap='YlGnBu')
    plt.title('Age Class vs Habitat Type (%)')
    plt.tight_layout()
    plt.show()

'''Визуализация данных. Многопанельные графики'''
print("\nМногопанельный график: обзор нескольких визуализаций.")
fig, axes = plt.subplots(2, 2, figsize=(15,10))

# Гистограмма длины
if 'Observed Length (m)' in df.columns:
    axes[0,0].hist(df['Observed Length (m)'].dropna(), bins=30, alpha=0.7, edgecolor='black')
    axes[0,0].set_title('Распределение длины')
    axes[0,0].set_xlabel('Length (m)')
    axes[0,0].set_ylabel('Частота')
    axes[0,0].grid(True, alpha=0.3)

# Scatter length vs weight
if all(col in df.columns for col in ['Observed Length (m)', 'Observed Weight (kg)']):
    axes[0,1].scatter(df['Observed Length (m)'], df['Observed Weight (kg)'], alpha=0.6)
    axes[0,1].set_title('Length vs Weight')
    axes[0,1].set_xlabel('Length (m)')
    axes[0,1].set_ylabel('Weight (kg)')
    axes[0,1].grid(True, alpha=0.3)

# Boxplot length by Common Name (top 6)
if 'Common Name' in df.columns and 'Observed Length (m)' in df.columns:
    top6 = df['Common Name'].value_counts().index[:6]
    df.boxplot(column='Observed Length (m)', by='Common Name', ax=axes[1,0], rot=45)
    axes[1,0].set_title('Length by Common Name')
    axes[1,0].set_xlabel('Common Name')

# Bar: counts by Habitat Type
if 'Habitat Type' in df.columns:
    df['Habitat Type'].value_counts().plot(kind='bar', ax=axes[1,1])
    axes[1,1].set_title('Habitat Type counts')
    axes[1,1].set_xlabel('Habitat Type')

plt.tight_layout()
plt.show()

'''Аналитические запросы'''
print("\n" + "="*60)
print("Аналитические запросы и ответы")
print("="*60)

# 1. Какой вид (Common Name) имеет наибольшую среднюю длину?
if 'Common Name' in df.columns and 'Observed Length (m)' in df.columns:
    avg_len_by_species = df.groupby('Common Name', observed=True)['Observed Length (m)'].agg(['mean','median','count']).sort_values('mean', ascending=False)
    print("\n1) Средняя длина по видам (топ 10):")
    print(avg_len_by_species.head(10))
    top_species = avg_len_by_species.index[0]
    top_len = avg_len_by_species.iloc[0]['mean']
    print(f"ОТВЕТ: Вид '{top_species}' имеет самую большую среднюю длину: {top_len:.2f} м")
    print("ИНТЕРПРЕТАЦИЯ: этот вид, вероятно, достигает больших размеров; возможно, это взрослые особи или крупные популяции.")

# 2. Есть ли связь между длиной и весом?
if 'Observed Length (m)' in df.columns and 'Observed Weight (kg)' in df.columns:
    corr = df['Observed Length (m)'].corr(df['Observed Weight (kg)'])
    print(f"\n2) Корреляция Length vs Weight: {corr:.3f}")
    print("ИНТЕРПРЕТАЦИЯ: высокая положительная корреляция указывает, что чем длиннее, тем тяжелее; если корр < 0.3 — влияние слабое.")

# 3. Как влияет возраст (Age Class) на длину?
if 'Age Class' in df.columns and 'Observed Length (m)' in df.columns:
    age_stats = df.groupby('Age Class', observed=True)['Observed Length (m)'].agg(['mean','median','count']).sort_values('mean', ascending=False)
    print("\n3) Средняя длина по возрастным классам:")
    print(age_stats)
    print("ИНТЕРПРЕТАЦИЯ: молодые особи обычно имеют меньшую длину, взрослые — большую (ожидаемо).")

# 4. В каких странах наблюдаются самые крупные особи?
if 'Country/Region' in df.columns and 'Observed Length (m)' in df.columns:
    country_len = df.groupby('Country/Region', observed=True)['Observed Length (m)'].mean().sort_values(ascending=False)
    print("\n4) Средняя длина по странам (топ 10):")
    print(country_len.head(10))
    print("ИНТЕРПРЕТАЦИЯ: факторы среды и локальные популяции влияют на средний размер.")

# 5. Есть ли сезонность в наблюдаемой длине/весе?
if 'Season' in df.columns and 'Observed Length (m)' in df.columns:
    season_stats = df.groupby('Season', observed=True)['Observed Length (m)'].agg(['mean','count'])
    print("\n5) Средняя длина по сезонам:")
    print(season_stats)
    print("ИНТЕРПРЕТАЦИЯ: сезонные изменения могут быть связаны с размножением, активностью или видимостью особей.")

# 6. Как пол (Sex) влияет на размер?
if 'Sex' in df.columns and 'Observed Length (m)' in df.columns:
    sex_stats = df.groupby('Sex', observed=True)['Observed Length (m)'].agg(['mean','median','count'])
    print("\n6) Длина по полу:")
    print(sex_stats)
    print("ИНТЕРПРЕТАЦИЯ: часто самцы/самки различаются по размерам; проверьте статистическую значимость при желании.")

# 7. Как распределяются размеры среди разных типов среды обитания?
if 'Habitat Type' in df.columns and 'Observed Length (m)' in df.columns:
    habitat_stats = df.groupby('Habitat Type', observed=True)['Observed Length (m)'].agg(['mean','median','count']).sort_values('mean', ascending=False)
    print("\n7) Средняя длина по типу среды:")
    print(habitat_stats.head(10))
    print("ИНТЕРПРЕТАЦИЯ: среда обитания (река/болото/прибрежье) влияет на ресурсы и условия роста.")

# 8. Есть ли зависимость между возрастом наблюдения (годом) и средней длиной (тренд)?
if 'Observation Year' in df.columns and 'Observed Length (m)' in df.columns:
    year_len = df.groupby('Observation Year', observed=True)['Observed Length (m)'].mean().dropna()
    print("\n8) Средняя длина по годам (последние 10):")
    print(year_len.tail(10))
    if len(year_len) > 2:
        trend = np.polyfit(year_len.index.astype(float), year_len.values, 1)[0]
        print(f"Тренд (наклон регрессии): {trend:.4f} м/год")
        if trend > 0.01:
            print("ОТВЕТ: Небольшой положительный тренд по годам.")
        elif trend < -0.01:
            print("ОТВЕТ: Небольшой отрицательный тренд.")
        else:
            print("ОТВЕТ: Стабильность по годам.")

# 9. Как conservation status связан с размерами?
if 'Conservation Status' in df.columns and 'Observed Length (m)' in df.columns:
    cons_stats = df.groupby('Conservation Status', observed=True)['Observed Length (m)'].agg(['mean','median','count']).sort_values('mean', ascending=False)
    print("\n9) Длина по статусу сохранения:")
    print(cons_stats)
    print("ИНТЕРПРЕТАЦИЯ: различия могут указывать на влияние антропогенных факторов и отбора.")

# 10. Влияет ли наблюдатель (Observer Name) на измерения (систематическая ошибка)?
if 'Observer Name' in df.columns and 'Observed Length (m)' in df.columns:
    obs_stats = df.groupby('Observer Name', observed=True)['Observed Length (m)'].agg(['mean','std','count']).sort_values('count', ascending=False)
    print("\n10) Средняя длина по наблюдателям (топ 10 по количеству):")
    print(obs_stats.head(10))
    print("ИНТЕРПРЕТАЦИЯ: существенные различия могут указывать на методологию измерения или систематические ошибки.")



'''Выводы'''
print("\n" + "="*60)
print("ОБЩИЕ ВЫВОДЫ ПО АНАЛИЗУ:")
print("="*60)

# Небольшая автоматическая генерация выводов на основе найденных статистик
conclusions = []
# Пример выводов на основе корреляции длина-вес
if 'Observed Length (m)' in df.columns and 'Observed Weight (kg)' in df.columns:
    corr_lv = df['Observed Length (m)'].corr(df['Observed Weight (kg)'])
    conclusions.append(f"Корреляция длины и веса: {corr_lv:.2f} — {'сильная' if abs(corr_lv)>0.5 else 'умеренная' if abs(corr_lv)>0.3 else 'слабая'} связь.")
# По сезонности (пример)
if 'Season' in df.columns:
    if 'Observed Length (m)' in df.columns:
        s_stats = df.groupby('Season', observed=True)['Observed Length (m)'].mean()
        conclusions.append(f"Средняя длина по сезонам (Winter->Autumn): {s_stats.to_dict()}")
# По возрастным классам
if 'Age Class' in df.columns and 'Observed Length (m)' in df.columns:
    age_ordered = df.groupby('Age Class', observed=True)['Observed Length (m)'].mean().sort_values(ascending=False)
    conclusions.append(f"Возрастные классы по средней длине: {age_ordered.to_dict()}")

# Печать выводов
for c in conclusions:
    print("- " + c)

# Общие численные итоги
if 'Observed Length (m)' in df.columns:
    total_len = df['Observed Length (m)'].sum(skipna=True)
    avg_len = df['Observed Length (m)'].mean(skipna=True)
    count_obs = df['Observed Length (m)'].count()
    print(f"\nОбщая измеренная длина (сумма): {total_len:.2f} м")
    print(f"Средняя длина: {avg_len:.2f} м")
    print(f"Количество измерений длины: {count_obs}")
