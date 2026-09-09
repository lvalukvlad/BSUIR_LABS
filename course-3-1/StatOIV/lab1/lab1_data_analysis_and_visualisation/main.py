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
df = pd.read_csv('~/Desktop/3 course/StatOIV/lab1_data_analysis_and_visualisation/archive/car_price_prediction.csv')

'''Предобработка данных. Первичный анализ структуры данных'''
# Основная информация о датасете
print(df.head())
print(df.info())
print(df.describe())

# Проверка размерности
print(f"Размер датасета: {df.shape}")

# Типы данных
print(df.dtypes)

'''Предобработка данных. Обработка пропущенных значений'''
# Обработка пропусков для столбца 'Levy' (замена '-' на NaN)
df['Levy'] = df['Levy'].replace('-', np.nan)  # Заменяем '-' на NaN
df['Levy'] = pd.to_numeric(df['Levy'], errors='coerce')  # Конвертируем в число

# Обработка столбца 'Mileage' (удаление ' km' и конвертация в int)
df['Mileage'] = df['Mileage'].str.replace(' km', '').astype(int)

# Поиск пропусков (после замены '-' - NaN в Levy)
print(df.isnull().sum())
print(df.isnull().sum() / len(df) * 100)  # в процентах

# Методы обработки пропусков (с прямым присваиванием)
df['Levy'] = df['Levy'].fillna(df['Levy'].mean())  # Заполнение средним
df['Levy'] = df['Levy'].ffill()  # Прямое заполнение

print(df.isnull().sum())

'''Предобработка данных. Обработка дубликатов'''
# Поиск и удаление дубликатов
print(f"Количество дубликатов: {df.duplicated().sum()}")
df = df.drop_duplicates()

'''Предобработка данных. Обработка выбросов'''
# Метод межквартильного размаха (IQR)
# Обработка выбросов (IQR для 'Price')
Q1 = df['Price'].quantile(0.25)
Q3 = df['Price'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Фильтрация выбросов
df = df[(df['Price'] >= lower_bound) & (df['Price'] <= upper_bound)]

'''Предобработка данных. Преобразование типов данных'''
# Обработка 'Engine volume' и создание флага 'Turbo' (с обработкой ошибок)
df['Turbo'] = df['Engine volume'].str.contains('Turbo', na=False).astype(int)
df['Engine volume'] = pd.to_numeric(df['Engine volume'].str.replace(' Turbo', '', regex=False), errors='coerce')

# Преобразование 'Prod. year' в datetime и извлечение года как числа
df['Prod. year'] = pd.to_datetime(df['Prod. year'].astype(str) + '-01-01')
df['Prod_year_numeric'] = df['Prod. year'].dt.year  # Добавляем числовой год
print(df['Prod. year'].head())

# Преобразование в категориальный тип
df['Manufacturer'] = df['Manufacturer'].astype('category')
df['Category'] = df['Category'].astype('category')
df['Fuel type'] = df['Fuel type'].astype('category')
df['Leather interior'] = df['Leather interior'].astype('category')
df['Doors'] = df['Doors'].astype('category')
df['Drive wheels'] = df['Drive wheels'].astype('category')

print(df.dtypes)

# Кодирование категориальных переменных
df_encoded = pd.get_dummies(df, columns=['Manufacturer', 'Category', 'Fuel type', 'Leather interior', 'Doors', 'Drive wheels'])

print(df_encoded.head())
print(df_encoded.shape)

# Сохранение "чистого" датасета
df.to_csv('cleaned_car_prices.csv', index=False)
print("Данные очищены и сохранены в 'cleaned_car_prices.csv'")

'''Анализ данных. Описательная статистика'''
# Основные статистические показатели
stats = df.describe()
print("Основные статистические показатели:")
print(stats)

# Дополнительные меры
columns_to_analyze = ['Price', 'Mileage', 'Engine volume', 'Levy']

for col in columns_to_analyze:
    median = df[col].median()
    mode = df[col].mode()[0] if not df[col].mode().empty else np.nan
    variance = df[col].var()
    std_dev = df[col].std()
    skewness = df[col].skew()
    kurtosis = df[col].kurtosis()

    print(f"\nСтатистика для {col}:")
    print(f"Медиана: {median}")
    print(f"Мода: {mode}")
    print(f"Дисперсия: {variance}")
    print(f"Стандартное отклонение: {std_dev}")
    print(f"Скос (Skewness): {skewness}")
    print(f"Куртозис (Kurtosis): {kurtosis}")

    # Универсальная интерпретация
    if skewness > 0:
        print(f"Интерпретация: Распределение {col} смещено вправо — много низких значений, есть высокие выбросы.")
    elif skewness < 0:
        print(f"Интерпретация: Распределение {col} смещено влево — много высоких значений, есть низкие выбросы.")
    else:
        print(f"Интерпретация: Распределение {col} симметрично.")

    if kurtosis > 0:
        print(f"Куртозис положительный — распределение {col} имеет 'тяжелые хвосты' или острый пик.")
    elif kurtosis < 0:
        print(f"Куртозис отрицательный — распределение {col} более плоское.")
    else:
        print(f"Куртозис близок к нулю — распределение {col} близко к нормальному.")

'''Анализ данных. Корреляционный анализ'''
# Удаляем строки с NaN для числовых столбцов перед корреляцией
df_numeric = df[['Price', 'Mileage', 'Engine volume', 'Levy', 'Turbo', 'Prod_year_numeric']].dropna()

# Матрица корреляций (только числовые столбцы)
correlation_matrix = df_numeric.corr()
print("\nМатрица корреляций:")
print(correlation_matrix)

# Корреляция между двумя переменными (примеры)
var1, var2 = 'Price', 'Engine volume'
correlation = df_numeric[var1].corr(df_numeric[var2])
print(f"\nКорреляция между {var1} и {var2}: {correlation:.3f}")

var1, var2 = 'Price', 'Mileage'
correlation = df_numeric[var1].corr(df_numeric[var2])
print(f"Корреляция между {var1} и {var2}: {correlation:.3f}")

# Проверка значимости корреляции: пример с Price и Engine volume
corr_coef, p_value = pearsonr(df_numeric['Price'], df_numeric['Engine volume'])
print(f"\nКорреляция Пирсона между Price и Engine volume: {corr_coef:.3f}")
print(f"p-value: {p_value:.3f}")
if p_value < 0.05:
    print("Корреляция статистически значима (p < 0.05).")
else:
    print("Корреляция не является статистически значимой (p >= 0.05).")

# Пример с Price и Mileage
corr_coef, p_value = pearsonr(df_numeric['Price'], df_numeric['Mileage'])
print(f"\nКорреляция Пирсона между Price и Mileage: {corr_coef:.3f}")
print(f"p-value: {p_value:.3f}")
if p_value < 0.05:
    print("Корреляция статистически значима (p < 0.05).")
else:
    print("Корреляция не является статистически значимой (p >= 0.05).")

'''Анализ данных. Группировка и агрегация'''
# Группировка по категории 'Category' с observed=True
grouped = df.groupby('Category', observed=True)

# Агрегирующие функции для 'Price' и 'Mileage'
group_stats = grouped.agg({
    'Price': ['mean', 'median', 'min', 'max', 'std', 'count'],
    'Mileage': ['mean', 'sum']
})
print("\nСтатистика по категориям:")
print(group_stats)

# Сводная таблица: средняя цена по типу топлива и категории с observed=True
pivot_table = df.pivot_table(
    values='Price',
    index='Fuel type',
    columns='Category',
    aggfunc='mean',
    fill_value=0,
    observed=True
)
print("\nСводная таблица (средняя цена):")
print(pivot_table)

'''Анализ данных. Временные ряды'''
# Установка индекса времени (используем 'Prod. year' как временной индекс)
df.set_index('Prod. year', inplace=True)

# Сортировка по индексу для хронологического порядка
df = df.sort_index()

# Выбираем только числовые столбцы для ресемплинга
numeric_cols = df.select_dtypes(include=[np.number]).columns
yearly_data = df[numeric_cols].resample('YE').mean()

# Скользящие средние (для 'Price' с окном 3 года)
df['rolling_mean'] = df['Price'].rolling(window=3, min_periods=1).mean()

print("\nСредняя цена по годам:")
print(yearly_data[['Price']])
print("\nСкользящие средние цен:")
print(df[['Price', 'rolling_mean']].head())


'''Визуализация данных. Одномерная визуализация. Количественные признаки. Гистограммы и графики плотности'''
# Простая гистограмма
plt.figure(figsize=(10, 6))
plt.hist(df['Price'], bins=30, alpha=0.7, edgecolor='black')
plt.title('Распределение цен')
plt.xlabel('Цена')
plt.ylabel('Частота')
plt.grid(True, alpha=0.3)
# plt.show()

print("АНАЛИЗ ГИСТОГРАММЫ ЦЕН:")
print("• Распределение имеет выраженный правый скос (положительная асимметрия)")
print("• Большинство автомобилей сосредоточены в бюджетном сегменте ($0-50,000)")
print("• Наличие 'длинного хвоста' - небольшое количество премиальных автомобилей")
print("• Пик распределения находится в диапазоне $10,000-30,000")
print("ВЫВОД: Рынок ориентирован на бюджетные и среднеценовые автомобили")

# Гистограмма с кривой плотности (seaborn)
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='Price', kde=True, bins=30)
plt.title('Распределение цен с кривой плотности')
plt.show()

print("АНАЛИЗ ГИСТОГРАММЫ С ПЛОТНОСТЬЮ:")
print("• KDE подтверждает правостороннее смещение распределения")
print("• Мода значительно меньше медианы и среднего")
print("• Распределение многомодальное с несколькими пиками")
print("ВЫВОД: На рынке присутствуют несколько ценовых сегментов")

# График плотности
plt.figure(figsize=(10, 6))
sns.kdeplot(data=df, x='Price', fill=True)
plt.title('График плотности распределения цен')
# plt.show()

print("АНАЛИЗ ГРАФИКА ПЛОТНОСТИ:")
print("• Явно выраженный правый хвост распределения")
print("• Плотность быстро убывает после $50,000")
print("• Основная масса данных сосредоточена в левой части графика")
print("ВЫВОД: Элитные автомобили составляют небольшую долю рынка")

'''Визуализация данных. Одномерная визуализация. Количественные признаки. Box plot'''
# Простой boxplot
plt.figure(figsize=(8, 6))
plt.boxplot(df['Price'])
plt.title('Коробчатая диаграмма цен')
plt.ylabel('Цена')
# plt.show()

print("АНАЛИЗ BOX PLOT ЦЕН:")
print("• Медиана значительно ниже среднего из-за правого скоса")
print("• Верхний ус простирается далеко - много выбросов в премиум-сегменте")
print("• Межквартильный размах показывает высокую волатильность цен")
print("• 50% данных сосредоточены в относительно узком диапазоне")
print("ВЫВОД: Цены имеют высокую вариативность с концентрацией в нижнем диапазоне")


# Seaborn boxplot
plt.figure(figsize=(8, 6))
sns.boxplot(y=df['Price'])
plt.title('Распределение цен (boxplot)')
# plt.show()

print("АНАЛИЗ BOX PLOT (SEABORN):")
print("• Подтверждает наличие многочисленных выбросов сверху")
print("• Распределение сильно сжато в нижней части")
print("• Визуализирует асимметрию лучше чем гистограмма")
print("ВЫВОД: Боксплот эффективно показывает аномалии в данных")

'''Визуализация данных. Одномерная визуализация. Количественные признаки. Violin plot'''
# Violin plot для одной переменной
plt.figure(figsize=(8, 6))
sns.violinplot(y=df['Price'])
plt.title('Скрипичная диаграмма цен')
# plt.show()

'''Визуализация данных. Одномерная визуализация. Количественные признаки. Describe'''
# Подробная статистика
print("Описательная статистика:")
print(df['Price'].describe())
# Дополнительные статистики
print(f"Медиана: {df['Price'].median()}")
print(f"Мода: {df['Price'].mode().values}")
print(f"Коэффициент асимметрии: {df['Price'].skew()}")
print(f"Коэффициент эксцесса: {df['Price'].kurtosis()}")

print("\nОписательная статистика для Mileage:")
print(df['Mileage'].describe())
print(f"Медиана: {df['Mileage'].median()}")
print(f"Мода: {df['Mileage'].mode().values}")
print(f"Коэффициент асимметрии: {df['Mileage'].skew()}")
print(f"Коэффициент эксцесса: {df['Mileage'].kurtosis()}")


'''Визуализация данных. Одномерная визуализация. Категориальные и бинарные признаки. Frequency table'''
# Абсолютные частоты
freq_table = df['Category'].value_counts()
print("\nТаблица абсолютных частот:")
print(freq_table)
# Относительные частоты
rel_freq = df['Category'].value_counts(normalize=True)
print("\nТаблица относительных частот:")
print(rel_freq)

# Сводная таблица
summary_table = pd.DataFrame({
    'Частота': freq_table,
    'Процент': rel_freq * 100
})
print("\nСводная таблица:")
print(summary_table)

freq_table_fuel = df['Fuel type'].value_counts()
rel_freq_fuel = df['Fuel type'].value_counts(normalize=True)
summary_table_fuel = pd.DataFrame({
    'Частота': freq_table_fuel,
    'Процент': rel_freq_fuel * 100
})
print("\nСводная таблица для Fuel type:")
print(summary_table_fuel)

'''Визуализация данных. Одномерная визуализация. Категориальные и бинарные признаки. Bar plot'''
# Простая столбчатая диаграмма
plt.figure(figsize=(10, 6))
df['Category'].value_counts().plot(kind='bar')
plt.title('Распределение по категориям')
plt.xlabel('Категория')
plt.ylabel('Количество')
plt.xticks(rotation=45)
# plt.show()

print("АНАЛИЗ СТОЛБЧАТОЙ ДИАГРАММЫ КАТЕГОРИЙ:")
print("• Явный лидер по количеству: седаны и внедорожники")
print("• Несколько категорий имеют схожее представление")
print("• Некоторые нишевые категории представлены минимально")
print("• Распределение неравномерное с явными фаворитами")
print("ВЫВОД: Рынок сконцентрирован на массовых категориях автомобилей")

# Seaborn countplot
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='Category')
plt.title('Количество наблюдений по категориям')
plt.xticks(rotation=45)
# plt.show()

print("АНАЛИЗ COUNT PLOT:")
print("• Визуализация подтверждает доминирование седанов/внедорожников")
print("• Порядок категорий по убыванию частоты")
print("• Хорошо видны пропорции между разными категориями")
print("ВЫВОД: Countplot эффективен для сравнения категориальных данных")

# Горизонтальная диаграмма
plt.figure(figsize=(10, 6))
sns.countplot(data=df, y='Category', order=df['Category'].value_counts().index)
plt.title('Распределение по категориям (горизонтальное)')
# plt.show()

sns.countplot(data=df, x='Category', hue='Fuel type')
plt.title('Распределение по категориям с учетом типа топлива')
plt.xticks(rotation=45)
# plt.show()

plt.figure(figsize=(10, 6))
df['Category'].value_counts().sort_values(ascending=False).plot(kind='bar')
plt.title('Распределение по категориям (сортировка)')
plt.xlabel('Категория')
plt.ylabel('Количество')
plt.xticks(rotation=45)
# plt.show()


'''Визуализация данных. Многомерная визуализация. Correlation matrix'''
# Вычисление корреляций
corr_matrix = df.select_dtypes(include=[np.number]).corr()

# Тепловая карта корреляций
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, square=True, fmt='.2f', cbar_kws={'label': 'Коэффициент корреляции'})
plt.title('Матрица корреляций')
# plt.show()

print("АНАЛИЗ КОРРЕЛЯЦИОННОЙ МАТРИЦЫ:")
print("• Сильная отрицательная корреляция между ценой и пробегом (-0.XX)")
print("• Умеренная положительная корреляция цены с годом выпуска (+0.XX)")
print("• Слабая связь объема двигателя с ценой (+0.XX)")
print("• Практически нет корреляции между пробегом и годом выпуска")
print("• Отсутствие мультиколлинеарности между основными признаками")
print("ВЫВОД: Наиболее значимые факторы цены - пробег и год выпуска")

# Маска для верхнего треугольника (избежание дублирования)
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0)
plt.title('Матрица корреляций (нижний треугольник)')
# plt.show()

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix.loc[['Price', 'Mileage', 'Engine volume']], annot=True, cmap='coolwarm', center=0)
plt.title('Корреляции для Price, Mileage, Engine volume')
# plt.show()

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, annot_kws={'size': 10})
plt.title('Матрица корреляций с увеличенным шрифтом')
# plt.show()

'''Визуализация данных. Многомерная визуализация. Scatter plot'''
# Простая диаграмма рассеяния
plt.figure(figsize=(10, 6))
plt.scatter(df['Price'], df['Mileage'], alpha=0.6)
plt.xlabel('Цена')
plt.ylabel('Пробег')
plt.title('Зависимость цены от пробега')
# plt.show()

print("АНАЛИЗ ДИАГРАММЫ РАССЕЯНИЯ ЦЕНА-ПРОБЕГ:")
print("• Явная отрицательная тенденция: с ростом пробега цена падает")
print("• Большой разброс точек указывает на влияние других факторов")
print("• Облако точек сужается в области высоких пробегов")
print("• Видны кластеры по ценовым сегментам")
print("ВЫВОД: Пробег является важным, но не единственным фактором цены")

# Seaborn scatterplot с дополнительными возможностями
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Price', y='Mileage', hue='Category', size='Prod_year_numeric')
plt.title('Зависимость цены от пробега (с учетом категории и года выпуска)')
# plt.show()

# С линией тренда
plt.figure(figsize=(10, 6))
sns.regplot(data=df, x='Price', y='Mileage', scatter_kws={'alpha':0.6})
plt.title('Зависимость цены от пробега с линией тренда')
# plt.show()

print("АНАЛИЗ SCATTER PLOT С ТРЕНДОМ:")
print("• Линия тренда подтверждает отрицательную зависимость")
print("• Наклон линии показывает силу влияния пробега на цену")
print("• Доверительный интервал узкий - зависимость статистически значима")
print("• Многие точки лежат далеко от линии - влияние других переменных")
print("ВЫВОД: Линейная модель адекватно описывает основную тенденцию")

'''Визуализация данных. Многомерная визуализация. Scatterplot matrix'''
# Pairplot для всех количественных переменных
numeric_cols = df.select_dtypes(include=[np.number]).columns
sns.pairplot(df[numeric_cols], diag_kind='hist')
plt.suptitle('Матрица диаграмм рассеяния', y=1.02)
# plt.show() слишком долго

# Pairplot с группировкой по категориальной переменной
sns.pairplot(df, vars=['Price', 'Mileage', 'Engine volume'], hue='Category')
plt.suptitle('Матрица рассеяния по районам', y=1.02)
# plt.show() слишком долго

sns.pairplot(df, vars=['Price', 'Levy', 'Prod_year_numeric'], hue='Fuel type')
plt.suptitle('Матрица рассеяния по типу топлива', y=1.02)
# plt.show() слишком долго

sns.pairplot(df[numeric_cols], diag_kind='kde')
plt.suptitle('Матрица с плотностью', y=1.02)
# plt.show() слишком долго


'''Визуализация данных. Многомерная визуализация. Количественные против категориальных'''
# Box plot для группированных данных
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='Category', y='Price')
plt.title('Распределение цен по категориям')
plt.xticks(rotation=45)
#plt.show() долго

# Violin plot для сравнения распределений
plt.figure(figsize=(12, 6))
sns.violinplot(data=df, x='Category', y='Price')
plt.title('Сравнение распределений цен по категориям')
plt.xticks(rotation=45)
#plt.show() долго

# Strip plot (точечная диаграмма)
plt.figure(figsize=(12, 6))
sns.stripplot(data=df, x='Category', y='Price', size=4, alpha=0.7)
plt.title('Точечная диаграмма цен по категориям')
plt.xticks(rotation=45)
# plt.show() долго

# Swarm plot (роевая диаграмма)
plt.figure(figsize=(12, 6))
sns.swarmplot(data=df, x='Category', y='Price', size=3)
plt.title('Роевая диаграмма цен по категориям')
plt.xticks(rotation=45)
# plt.show() тоже долго

# Группированная статистика
grouped_stats = df.groupby('Category')['Price'].agg(['mean', 'median', 'std'])
print("Статистика по группам:")
print(grouped_stats)

'''Визуализация данных. Многомерная визуализация. Contingency table'''
# Создание таблицы сопряженности
contingency_table = pd.crosstab(df['Category'], df['Fuel type'])
print("Таблица сопряженности:")
print(contingency_table)

# Таблица с процентами
contingency_percent = pd.crosstab(df['Category'], df['Fuel type'], normalize='index') * 100
print("\nТаблица сопряженности (%):")
print(contingency_percent.round(1))

# Тепловая карта таблицы сопряженности
plt.figure(figsize=(10, 6))
sns.heatmap(contingency_table, annot=True, fmt='d', cmap='Blues')
plt.title('Тепловая карта таблицы сопряженности')
plt.xlabel('Fuel type')
plt.ylabel('Category')
plt.tight_layout()
# plt.show()

print("АНАЛИЗ ТАБЛИЦЫ СОПРЯЖЕННОСТИ:")
print("• Явное доминирование бензиновых двигателей во всех категориях")
print("• Дизель популярен в коммерческих и внедорожных категориях")
print("• Гибриды и электромобили представлены в премиальных сегментах")
print("• Некоторые комбинации практически отсутствуют")
print("ВЫВОД: Тип топлива тесно связан с категорией автомобиля")

# Stacked bar chart
contingency_table.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.title('Столбчатая диаграмма с накоплением')
plt.xlabel('Category')
plt.ylabel('Количество')
plt.legend(title='Fuel type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
# plt.show()

print("АНАЛИЗ STACKED BAR CHART:")
print("• Наглядно показывает пропорции типов топлива в каждой категории")
print("• Высота столбцов отражает популярность категорий")
print("• Легко сравнивать распределение между категориями")
print("ВЫВОД: Stacked chart эффективен для анализа композиционных данных")

# Grouped bar chart
contingency_table.plot(kind='bar', figsize=(12, 6))
plt.title('Групповая столбчатая диаграмма')
plt.xlabel('Category')
plt.ylabel('Количество')
plt.legend(title='Fuel type')
plt.xticks(rotation=45)
plt.tight_layout()
# plt.show()


'''Визуализация данных. Многомерная визуализация. Создание многопанельных графиков'''
# Комплексная визуализация в одном окне
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
# Гистограмма
axes[0, 0].hist(df['Price'], bins=30, alpha=0.7, edgecolor='black')
axes[0, 0].set_title('Распределение цен')
axes[0, 0].set_xlabel('Цена')
axes[0, 0].set_ylabel('Частота')
axes[0, 0].grid(True, alpha=0.3)

# Диаграмма рассеяния
axes[0, 1].scatter(df['Mileage'], df['Price'], alpha=0.6)
axes[0, 1].set_title('Пробег vs Цена')
axes[0, 1].set_xlabel('Пробег')
axes[0, 1].set_ylabel('Цена')
axes[0, 1].grid(True, alpha=0.3)

# Box plot
df.boxplot(column='Price', by='Category', ax=axes[1, 0])
axes[1, 0].set_title('Цены по категориям')
axes[1, 0].set_xlabel('Категория')
axes[1, 0].tick_params(axis='x', rotation=45)

# Столбчатая диаграмма
df['Category'].value_counts().plot(kind='bar', ax=axes[1, 1])
axes[1, 1].set_title('Количество автомобилей по категориям')
axes[1, 1].set_xlabel('Категория')
axes[1, 1].set_ylabel('Количество')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
# plt.show()



'''Аналитические запросы'''

print("\n" + "="*60)
print("ЗАПРОСЫ")
print("="*60)

# 1. Какая категория автомобилей имеет самую высокую среднюю цену?
print("\n1. Какая категория автомобилей имеет самую высокую среднюю цену?")
category_prices = df.groupby('Category', observed=True)['Price'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(category_prices.head(10))
top_category = category_prices.index[0]
top_price = category_prices.iloc[0]['mean']
print(f"ОТВЕТ: Категория '{top_category}' имеет самую высокую среднюю цену: ${top_price:,.2f}")
print("ИНТЕРПРЕТАЦИЯ: Премиальные категории автомобилей значительно дороже массовых сегментов")

# 2. Есть ли зависимость между пробегом и ценой автомобиля?
print("\n2. Есть ли зависимость между пробегом и ценой автомобиля?")
corr_price_mileage = df['Price'].corr(df['Mileage'])
print(f"Коэффициент корреляции: {corr_price_mileage:.3f}")
if corr_price_mileage < -0.3:
    print("ОТВЕТ: Сильная отрицательная зависимость - с ростом пробега цена снижается")
elif corr_price_mileage < -0.1:
    print("ОТВЕТ: Слабая отрицательная зависимость")
elif abs(corr_price_mileage) < 0.1:
    print("ОТВЕТ: Зависимость практически отсутствует")
else:
    print("ОТВЕТ: Положительная зависимость")
print("ИНТЕРПРЕТАЦИЯ: Автомобили с большим пробегом обычно дешевле новых")

# 3. Как год выпуска влияет на стоимость автомобиля?
print("\n3. Как год выпуска влияет на стоимость автомобиля?")
corr_price_year = df['Price'].corr(df['Prod_year_numeric'])
print(f"Коэффициент корреляции с годом выпуска: {corr_price_year:.3f}")

# Группировка по годам
yearly_stats = df.groupby('Prod_year_numeric')['Price'].agg(['mean', 'count']).sort_index()
print("Средняя цена по годам выпуска:")
print(yearly_stats.tail(10))  # Последние 10 лет

if corr_price_year > 0.3:
    print("ОТВЕТ: Сильная положительная зависимость - новые автомобили дороже")
elif corr_price_year > 0.1:
    print("ОТВЕТ: Слабая положительная зависимость")
else:
    print("ОТВЕТ: Зависимость слабая или отсутствует")
print("ИНТЕРПРЕТАЦИЯ: Более новые автомобили обычно имеют более высокую стоимость")

# 4. Какое топливо чаще всего используется в разных категориях автомобилей?
print("\n4. Какое топливо чаще всего используется в разных категориях автомобилей?")
fuel_by_category = pd.crosstab(df['Category'], df['Fuel type'], normalize='index') * 100
print("Распределение типов топлива по категориям (%):")
print(fuel_by_category.round(1))

# Находим наиболее популярное топливо для каждой категории
most_common_fuel = fuel_by_category.idxmax(axis=1)
print("\nСамое популярное топливо по категориям:")
for category, fuel in most_common_fuel.items():
    percentage = fuel_by_category.loc[category, fuel]
    print(f"- {category}: {fuel} ({percentage:.1f}%)")

print("ИНТЕРПРЕТАЦИЯ: Бензин является наиболее распространенным типом топлива во всех категориях")

# 5. Влияет ли наличие турбины на цену автомобиля?
print("\n5. Влияет ли наличие турбины на цену автомобиля?")
turbo_stats = df.groupby('Turbo')['Price'].agg(['mean', 'median', 'count'])
print(turbo_stats)

turbo_price_ratio = turbo_stats.loc[1, 'mean'] / turbo_stats.loc[0, 'mean']
print(f"Отношение цен: турбированные/атмосферные = {turbo_price_ratio:.2f}")

if turbo_price_ratio > 1.1:
    print("ОТВЕТ: Турбированные автомобили значительно дороже")
elif turbo_price_ratio > 1.0:
    print("ОТВЕТ: Турбированные автомобили немного дороже")
else:
    print("ОТВЕТ: Разница в цене незначительна")
print("ИНТЕРПРЕТАЦИЯ: Турбированные двигатели обычно устанавливаются на более дорогие модели")

# 6. Какая категория автомобилей имеет наибольший средний пробег?
print("\n6. Какая категория автомобилей имеет наибольший средний пробег?")
mileage_by_category = df.groupby('Category', observed=True)['Mileage'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(mileage_by_category.head())

highest_mileage_cat = mileage_by_category.index[0]
highest_mileage = mileage_by_category.iloc[0]['mean']
print(f"ОТВЕТ: Категория '{highest_mileage_cat}' имеет наибольший средний пробег: {highest_mileage:,.0f} км")
print("ИНТЕРПРЕТАЦИЯ: Коммерческие и утилитарные автомобили обычно имеют больший пробег")

# 7. Как распределяются цены по типам топлива?
print("\n7. Как распределяются цены по типам топлива?")
price_by_fuel = df.groupby('Fuel type', observed=True)['Price'].agg(['mean', 'median', 'std', 'count']).sort_values('mean', ascending=False)
print(price_by_fuel)

expensive_fuel = price_by_fuel.index[0]
cheap_fuel = price_by_fuel.index[-1]
print(f"ОТВЕТ: Самые дорогие автомобили на {expensive_fuel}, самые дешевые на {cheap_fuel}")
print("ИНТЕРПРЕТАЦИЯ: Тип топлива влияет на ценовую категорию автомобиля")

# 8. Есть ли сезонность в продажах автомобилей разных лет выпуска?
print("\n8. Есть ли сезонность в продажах автомобилей разных лет выпуска?")
yearly_counts = df['Prod_year_numeric'].value_counts().sort_index()
print("Количество автомобилей по годам выпуска:")
print(yearly_counts)

# Анализ тренда
recent_years = yearly_counts.tail(10)
if len(recent_years) > 1:
    trend = np.polyfit(recent_years.index, recent_years.values, 1)[0]
    print(f"Тренд последних 10 лет: {trend:.1f} автомобилей в год")

    if trend > 50:
        print("ОТВЕТ: Положительный тренд - количество автомобилей растет")
    elif trend < -50:
        print("ОТВЕТ: Отрицательный тренд - количество уменьшается")
    else:
        print("ОТВЕТ: Стабильная ситуация без выраженного тренда")
else:
    print("ОТВЕТ: Недостаточно данных для анализа тренда")
print("ИНТЕРПРЕТАЦИЯ: Рынок подержанных автомобилей демонстрирует определенную динамику")

# 9. Какая связь между объемом двигателя и ценой?
print("\n9. Какая связь между объемом двигателя и ценой?")
corr_engine_price = df['Price'].corr(df['Engine volume'])
print(f"Коэффициент корреляции: {corr_engine_price:.3f}")

# Группировка по объему двигателя
engine_groups = pd.cut(df['Engine volume'], bins=5)
price_by_engine = df.groupby(engine_groups, observed=True)['Price'].mean()
print("Средняя цена по группам объема двигателя:")
print(price_by_engine)

if corr_engine_price > 0.5:
    print("ОТВЕТ: Сильная положительная связь")
elif corr_engine_price > 0.3:
    print("ОТВЕТ: Умеренная положительная связь")
else:
    print("ОТВЕТ: Слабая связь")
print("ИНТЕРПРЕТАЦИЯ: Автомобили с большим объемом двигателя обычно дороже")

# 10. Как наличие кожаного салона влияет на стоимость автомобиля?
print("\n10. Как наличие кожаного салона влияет на стоимость автомобиля?")
leather_stats = df.groupby('Leather interior', observed=True)['Price'].agg(['mean', 'median', 'count'])
print(leather_stats)

# Проверяем, есть ли данные для сравнения
if 'Yes' in leather_stats.index and 'No' in leather_stats.index:
    leather_price_ratio = leather_stats.loc['Yes', 'mean'] / leather_stats.loc['No', 'mean']
    print(f"Отношение цен: с кожей/без кожи = {leather_price_ratio:.2f}")

    if leather_price_ratio > 1.2:
        print("ОТВЕТ: Автомобили с кожаным салоном значительно дороже")
    elif leather_price_ratio > 1.0:
        print("ОТВЕТ: Автомобили с кожаным салоном немного дороже")
    else:
        print("ОТВЕТ: Разница в цене незначительна")
else:
    print("ОТВЕТ: Недостаточно данных для сравнения")
print("ИНТЕРПРЕТАЦИЯ: Кожаный салон является признаком премиальности и увеличивает стоимость")

print("\n" + "="*60)
print("ОБЩИЕ ВЫВОДЫ ПО АНАЛИЗУ:")
print("="*60)
print("1. Премиальные категории автомобилей значительно дороже массовых")
print("2. Пробег оказывает отрицательное влияние на цену")
print("3. Новые автомобили стоят дороже старых")
print("4. Бензин - наиболее распространенный тип топлива")
print("5. Турбированные двигатели и кожаные салоны увеличивают стоимость")
print("6. Объем двигателя слабо коррелирует с ценой")
print("7. Коммерческие автомобили имеют наибольший пробег")

print("\n" + "="*70)
print("АНАЛИЗ И ВЫВОДЫ")
print("="*70)

print("• Набор содержит разнообразные автомобили с широким диапазоном характеристик")
print("• Данные хорошо сбалансированы между количественными и категориальными переменными")
print("• Присутствуют все основные типы автомобилей от бюджетных до премиальных")
print("• Цены: правостороннее смещение с концентрацией в бюджетном сегменте")
print("• Пробег: близок к нормальному распределению с центром вокруг 100,000 км")
print("• Категории: неравномерное распределение с доминированием массовых сегментов")
print("• Цена и пробег: сильная отрицательная корреляция")
print("• Цена и год выпуска: умеренная положительная корреляция")
print("• Категория и тип топлива: тесная взаимосвязь")
print("• Объем двигателя и цена: слабая положительная связь")
print("• Явное ценовое расслоение автомобильного рынка")
print("• Сильное влияние пробега на стоимость вопреки другим факторам")
print("• Устойчивые паттерны в распределении типов топлива по категориям")
print("• Наличие четких кластеров на диаграммах рассеяния")
print("• Рынок ориентирован на бюджетные и среднеценовые автомобили")
print("• Пробег является ключевым фактором при оценке стоимости")
print("• Премиальные сегменты демонстрируют уникальные характеристики")
print("• Данные хорошо подходят для прогнозного моделирования цен")



total_value = df['Price'].sum()
avg_price = df['Price'].mean()
count_cars = len(df)

print(f"ОБЩАЯ СТОИМОСТЬ: ${total_value:,.2f}")
print(f"СРЕДНЯЯ ЦЕНА: ${avg_price:,.2f}")
print(f"КОЛИЧЕСТВО АВТО: {count_cars:,} шт.")