import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, PolynomialFeatures, FunctionTransformer, OneHotEncoder, OrdinalEncoder, SplineTransformer
from sklearn.model_selection import KFold, train_test_split, cross_validate, cross_val_predict, cross_val_score, GridSearchCV, RandomizedSearchCV
from optbinning import OptimalBinning
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, SimpleImputer, IterativeImputer
from sklearn.datasets import make_blobs
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNetCV, RidgeCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from scipy.stats import loguniform
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from datetime import datetime

# Загрузка датасета
data_raw = pd.read_csv('spotify_songs.csv')
print("Исходные данные:")
print(data_raw.info())
print(f"Размер: {data_raw.shape}")

numeric_cols = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                'duration_ms', 'track_popularity']

print("Пропуски:", data_raw[numeric_cols].isnull().sum())

data_for_outliers = data_raw.copy()
data_for_outliers['track_name'] = data_for_outliers['track_name'].fillna('unknown')
data_for_outliers['track_artist'] = data_for_outliers['track_artist'].fillna('unknown')
data_for_outliers['track_album_name'] = data_for_outliers['track_album_name'].fillna('unknown')
data_raw['track_age'] = (pd.to_datetime('2025-10-28') - pd.to_datetime(data_raw['track_album_release_date'], errors='coerce')).dt.days
data_raw['energy_acoustic_ratio'] = data_raw['energy'] / (data_raw['acousticness'] + 1e-10)  # Избегаем деления на 0
data_raw['tempo_binned'] = pd.qcut(data_raw['tempo'], q=5, labels=False, duplicates='drop').astype(float)

# Статистика по исполнителю
artist_stats = data_raw.groupby('track_artist')['track_popularity'].agg(
    artist_mean_pop='mean',
    artist_max_pop='max',
    artist_track_count='count'
).reset_index()

data_raw = data_raw.merge(artist_stats, on='track_artist', how='left')

# Заполняем NaN в новых признаках по артисту (если артист не встречался в данных при расчёте статистики)
data_raw['artist_mean_pop'].fillna(data_raw['artist_mean_pop'].mean(), inplace=True)
data_raw['artist_max_pop'].fillna(data_raw['artist_max_pop'].max(), inplace=True)
data_raw['artist_track_count'].fillna(1, inplace=True)

# Обновляем список числовых колонок
numeric_cols = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                'duration_ms', 'track_popularity', 'track_age', 'energy_acoustic_ratio', 'tempo_binned',
                'artist_mean_pop', 'artist_max_pop', 'artist_track_count']
print("Обновлённый список числовых колонок:", numeric_cols)
print("Пропуски:", data_raw[numeric_cols].isnull().sum())

### 1.1 Масштабирование и нормализация признаков
feature = np.array([[-500.5], [-100.1], [0], [100.1], [900.9]])
minmax_scaler = MinMaxScaler(feature_range=(0, 1))
scaled_feature = minmax_scaler.fit_transform(feature)
print("1.1 MinMaxScaler результат:", scaled_feature)

### 1.2 Стандартизация признака (Z-оценка)
x = np.array([[-1000.1], [-200.2], [500.5], [600.6], [9000.9]])
scaler = StandardScaler()
standardized = scaler.fit_transform(x)
print("1.2 StandardScaler результат:", standardized)
print("Среднее:", round(standardized.mean(), 2))
print("Стандартное отклонение:", round(standardized.std(), 2))

### 1.3 Работа с выбросами
robust_scaler = RobustScaler()
robust_scaled = robust_scaler.fit_transform(x)
print("1.3 RobustScaler результат:", robust_scaled)

### 1.4 Генерирование полиномиальных и взаимодействующих признаков
features = np.array([[2, 3], [2, 3], [2, 3]])
polynomial_interaction = PolynomialFeatures(degree=2, include_bias=False)
poly_features = polynomial_interaction.fit_transform(features)
print("1.4 Полиномиальные признаки:", poly_features)
interaction = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
interaction_features = interaction.fit_transform(features)
print("Взаимодействия:", interaction_features)

### 1.5 Преобразование существующих признаков
features = np.array([[2, 3], [2, 3], [2, 3]])
print("1.5 Исходные данные:", features)
def add_ten(x): return x + 10
ten_transformer = FunctionTransformer(add_ten, validate=True)
transformed_features = ten_transformer.fit_transform(features)
print("Результат преобразования (каждый элемент +10):", transformed_features)
print("Проверка:", [[2+10, 3+10], [2+10, 3+10], [2+10, 3+10]])

# Подготовка данных с новыми признаками

data_raw['track_age'].fillna(data_raw['track_age'].median(), inplace=True)

# Определим признаки X и целевую переменную y
X_raw = data_raw.drop([
    'track_popularity', 'track_id', 'track_name', 'track_artist',
    'track_album_id', 'track_album_name', 'playlist_id',
    'playlist_name', 'track_album_release_date'
], axis=1, errors='ignore')

y_raw = data_raw['track_popularity']

# Разделение на обучающую и тестовую выборки
X_train_raw, X_test_raw, y_train, y_test = train_test_split(X_raw, y_raw, test_size=0.2, random_state=42)

# Кодирование категориальных признаков
X_train_encoded = pd.get_dummies(X_train_raw, columns=['playlist_genre', 'playlist_subgenre'], drop_first=True)
X_test_encoded = pd.get_dummies(X_test_raw, columns=['playlist_genre', 'playlist_subgenre'], drop_first=True)

# Убедимся, что тестовая выборка имеет те же колонки, что и обучающая
X_test_encoded = X_test_encoded.reindex(columns=X_train_encoded.columns, fill_value=0)
X_train_encoded['log_duration_ms'] = np.log1p(X_train_raw['duration_ms'])
X_test_encoded['log_duration_ms'] = np.log1p(X_test_raw['duration_ms'])

# Стандартизация числовых признаков
numeric_features = X_train_encoded.select_dtypes(include=[np.number]).columns
scaler = StandardScaler()
X_train_scaled = X_train_encoded.copy()
X_train_scaled[numeric_features] = scaler.fit_transform(X_train_encoded[numeric_features])

X_test_scaled = X_test_encoded.copy()
X_test_scaled[numeric_features] = scaler.transform(X_test_encoded[numeric_features])

X_train_final_scaled = X_train_scaled
X_test_final_scaled = X_test_scaled

### 1.6 Обработка выбросов
### filtered_outliers = data_for_outliers[(data_for_outliers['duration_ms'] >= 30000) &
###                                     (data_for_outliers['duration_ms'] <= 600000)]
data_raw['log_duration_ms'] = np.log1p(data_raw['duration_ms'])
# print(f"1.6 Исходно: {len(data_for_outliers)}, после фильтрации: {len(filtered_outliers)}")
#data_for_outliers["outlier_duration"] = np.where(
 #   (data_for_outliers["duration_ms"] < 30000) | (data_for_outliers["duration_ms"] > 600000), 1, 0)
# print("Выбросы по длительности:", data_for_outliers["outlier_duration"].sum())
data_for_outliers["log_duration_ms"] = [np.log(x) for x in data_for_outliers["duration_ms"]]
# print(data_for_outliers[['duration_ms', 'log_duration_ms', 'outlier_duration']].head())
# Используем исходные данные БЕЗ удаления выбросов (но с новыми признаками!)
X_raw = data_raw.drop(['track_popularity', 'track_id', 'track_name', 'track_artist',
                       'track_album_id', 'track_album_name', 'playlist_id',
                       'playlist_name', 'track_album_release_date'], axis=1, errors='ignore')
y_raw = data_raw['track_popularity']
categorical_features = ['playlist_genre', 'playlist_subgenre']

for col in categorical_features:
    data_raw[col] = data_raw[col].fillna('unknown')

feature_cols = [col for col in data_raw.columns if col not in [
    'track_popularity', 'track_id', 'track_name', 'track_artist',
    'track_album_id', 'track_album_name', 'playlist_id',
    'playlist_name', 'track_album_release_date'
]]

X = data_raw[feature_cols].copy()
y = data_raw['track_popularity']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Указываем индексы категориальных признаков для CatBoost
cat_features_indices = [X_train.columns.get_loc(col) for col in categorical_features if col in X_train.columns]

### 1.6.1 Визуализация выбросов
plt.figure(figsize=(10, 6))
sns.boxplot(data=data_raw['duration_ms'])
plt.title('Boxplot длительности треков (до фильтрации)')
plt.xlabel('duration_ms')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(data=data_raw['duration_ms'])
plt.title('Boxplot длительности треков (после фильтрации)')
plt.xlabel('duration_ms')
plt.show()

"""### 1.7 Дискретизация признаков
tempo = X_train_raw['tempo'].values
popularity = y_train.values
optb_tempo = OptimalBinning(name="tempo", dtype="numerical", solver="cp")
optb_tempo.fit(tempo, popularity)
tempo_binned_train = optb_tempo.transform(tempo, metric="bins")
tempo_test = X_test_raw['tempo'].values
tempo_binned_test = optb_tempo.transform(tempo_test, metric="bins")
X_train_scaled['tempo_binned'] = tempo_binned_train
X_test_scaled['tempo_binned'] = tempo_binned_test
print(f"Train shape после добавления: {X_train_scaled.shape}")
print(f"Test shape после добавления: {X_test_scaled.shape}")
"""
### 1.8 Удаление наблюдений с пропущенных значений
data_with_nans = data_raw.copy()
data_no_nans = data_with_nans.dropna()
print(f"Исходно: {len(data_with_nans)} строк, после удаления: {len(data_no_nans)} строк")
print("Размер очищенных данных:", data_no_nans.shape)

### 1.9 Заполнение пропущенных значений
data_with_nans = data_raw.copy()
numeric_data = data_with_nans[numeric_cols].values
scaler = StandardScaler()
standardized_numeric = scaler.fit_transform(numeric_data)
true_value = standardized_numeric[0, 0]
standardized_numeric[0, 0] = np.nan
imputer = KNNImputer(n_neighbors=5)
numeric_imputed = imputer.fit_transform(standardized_numeric)
print("Истинное значение danceability:", true_value)
print("Заполненное значение danceability:", numeric_imputed[0, 0])

### 2.1 Кодирование номинальных категориальных признаков
data_encoded = pd.get_dummies(data_raw[['playlist_genre', 'playlist_subgenre']], drop_first=True)
print("Размер закодированных данных:", data_encoded.shape)

### 2.1 Кодирование номинальных категориальных признаков (исправленная версия)
encoder = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
categorical_cols = ['playlist_genre', 'playlist_subgenre']

# Преобразование категориальных признаков
encoded_categorical_train = encoder.fit_transform(X_train_raw[categorical_cols])
encoded_categorical_test = encoder.transform(X_test_raw[categorical_cols])

numeric_features_for_merge = X_train_scaled.select_dtypes(include=[np.number]).columns.drop('tempo_binned', errors='ignore')
X_train_combined = np.hstack((X_train_scaled[numeric_features_for_merge].values, encoded_categorical_train))
X_test_combined = np.hstack((X_test_scaled[numeric_features_for_merge].values, encoded_categorical_test))

# Создаем новые DataFrame с объединенными признаками
feature_names = list(numeric_features_for_merge) + list(encoder.get_feature_names_out())
X_train_final = pd.DataFrame(X_train_combined, columns=feature_names, index=X_train_scaled.index)
X_test_final = pd.DataFrame(X_test_combined, columns=feature_names, index=X_test_scaled.index)

print(f"Train shape после кодирования: {X_train_final.shape}")
print(f"Test shape после кодирования: {X_test_final.shape}")

### 2.2 Кодирование порядковых категориальных признаков
categories = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]  # Порядок для ключа (key)
encoder = OrdinalEncoder(categories=categories)
data_raw["key_encoded"] = encoder.fit_transform(data_raw[["key"]])
print("Первые 5 строк с закодированным key:")
print(data_raw[["key", "key_encoded"]].head())

### 2.2.1 Создание нового признака
X_train_raw['energy_acoustic_ratio'] = X_train_raw['energy'] / (X_train_raw['acousticness'] + 1e-10)
X_test_raw['energy_acoustic_ratio'] = X_test_raw['energy'] / (X_test_raw['acousticness'] + 1e-10)

# Обновляем X_train_final и X_test_final
X_train_final['energy_acoustic_ratio'] = X_train_raw['energy_acoustic_ratio'].values
X_test_final['energy_acoustic_ratio'] = X_test_raw['energy_acoustic_ratio'].values

# Повторная стандартизация всех числовых признаков
numeric_features_final = X_train_final.select_dtypes(include=[np.number]).columns
scaler_final = StandardScaler()
X_train_final_scaled = X_train_final.copy()
X_train_final_scaled[numeric_features_final] = scaler_final.fit_transform(X_train_final[numeric_features_final])
X_test_final_scaled = X_test_final.copy()
X_test_final_scaled[numeric_features_final] = scaler_final.transform(X_test_final[numeric_features_final])

print(f"Final Train: {X_train_final_scaled.shape}, Final Test: {X_test_final_scaled.shape}")

### 2.3 Заполнение пропущенных значений классов

print("Пропуски в track_name до обработки:", data_raw["track_name"].isnull().sum())
imputer_freq = SimpleImputer(strategy="most_frequent")
track_name_filled_freq = imputer_freq.fit_transform(data_raw[["track_name"]])[:, 0]
data_raw["track_name_filled_freq"] = track_name_filled_freq

imputer_const = SimpleImputer(strategy="constant", fill_value="missing")
track_name_filled_const = imputer_const.fit_transform(data_raw[["track_name"]])[:, 0]
data_raw["track_name_filled_const"] = track_name_filled_const

print("Пропуски после обработки:")
print("track_name_filled_freq:", data_raw["track_name_filled_freq"].isnull().sum())
print("track_name_filled_const:", data_raw["track_name_filled_const"].isnull().sum())

print("\nПервые 5 строк с заполненными значениями (most_frequent):")
print(data_raw[["track_name", "track_name_filled_freq"]].head())

print("\nПервые 5 строк с заполненными значениями (missing):")
print(data_raw[["track_name", "track_name_filled_const"]].head())

### 3 Оценивание моделей
### 3.1 Кросс-валидация моделей
# Используем финальные данные
X = X_train_final_scaled
y = y_train

# Создать конвейер со стандартизатором
pipeline = make_pipeline(StandardScaler(), LinearRegression())
cv = KFold(n_splits=10, shuffle=True, random_state=1)

# Перекрёстная проверка
cv_results = cross_validate(
    pipeline,
    X,
    y,
    cv=cv,
    scoring=['r2', 'neg_mean_squared_error'],
    return_train_score=False,
    n_jobs=-1
)

# Средняя точность модели
print("\n3.1 Кросс-валидация моделей")
print("Средний R²:", cv_results['test_r2'].mean())
print("Средняя ошибка (MSE):", -cv_results['test_neg_mean_squared_error'].mean())

# Взглянуть на оценки для всех 10 блоков
print("\nОценки R² для всех 10 блоков:", cv_results['test_r2'])
print("Оценки MSE для всех 10 блоков:", -cv_results['test_neg_mean_squared_error'])

### 3.2 Метрики регрессионных моделей
# Используем финальные данные
X = X_train_final_scaled
y = y_train
# Создать объект линейной регрессии
ols = LinearRegression()
# Получить предсказания с помощью кросс-валидации
predictions = cross_val_predict(ols, X, y, cv=3)

# Вычислить среднеквадратичную ошибку (MSE)
mse = mean_squared_error(y, predictions)
print("\n3.2 Метрики регрессионных моделей")
print("Среднеквадратичная ошибка (MSE):", mse)
r2_scores = cross_val_score(ols, X, y, scoring="r2", cv=3)
print("R² для каждого фолда:", r2_scores)
print("Средний R²:", r2_scores.mean())

### 3.3 RandomForestRegressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train_final_scaled, y_train)
y_pred_rf = rf_model.predict(X_test_final_scaled)

### 4 Отбор модели
### 4.1 Отбор наилучших моделей с помощью исчерпывающего поиска
# Используем финальные данные
X = X_train_final_scaled
y = y_train
# Создать объект Ridge регрессии
ridge = Ridge()

# Создать диапазон вариантов значений регуляризационного гиперпараметра alpha
alpha = np.logspace(-3, 3, 10)
hyperparameters = dict(alpha=alpha)
# Создать объект решеточного поиска
gridsearch = GridSearchCV(ridge, hyperparameters, cv=5, scoring='r2', verbose=0)
best_model = gridsearch.fit(X, y)

# Вывести наилучшие гиперпараметры
print("\n4.1 Отбор наилучших моделей с помощью исчерпывающего поиска")
print("Лучший alpha:", best_model.best_estimator_.get_params()['alpha'])
print("Лучший R²:", best_model.best_score_)

# Предсказать вектор целей для тренировочных данных
predictions = best_model.predict(X)

### 4.2 Отбор наилучших моделей с помощью рандомизированного поиска
# Используем финальные данные
X = X_train_final_scaled
y = y_train

# Создать объект Ridge регрессии
ridge = Ridge()

# Создать диапазон вариантов значений регуляризационного гиперпараметра
alpha = loguniform(1e-3, 1e3)
hyperparameters = dict(alpha=alpha)
randomizedsearch = RandomizedSearchCV(
    ridge, hyperparameters, random_state=1, n_iter=100,
    cv=5, scoring='r2', verbose=0, n_jobs=-1
)
best_model = randomizedsearch.fit(X, y)

# Определить равномерное распределение между 0.001 и 1000, отобрать 10 значений
sample_alphas = loguniform(1e-3, 1e3).rvs(10, random_state=1)
print("\nПримеры значений alpha (10 выборок):", sample_alphas)

print("\n4.2 Отбор наилучших моделей с помощью рандомизированного поиска")
print("Лучший alpha:", best_model.best_estimator_.get_params()['alpha'])
print("Лучший R²:", best_model.best_score_)
predictions = best_model.predict(X)

### 4.3 Полная оценка качества моделей

# Linear Regression
regression = LinearRegression()
regression.fit(X_train_final_scaled, y_train)
y_pred_lr = regression.predict(X_test_final_scaled)
mae_lr = mean_absolute_error(y_test, y_pred_lr)
mse_lr = mean_squared_error(y_test, y_pred_lr)
rmse_lr = np.sqrt(mse_lr)
r2_lr = r2_score(y_test, y_pred_lr)

# RandomForest
rf_model.fit(X_train_final_scaled, y_train)
y_pred_rf = rf_model.predict(X_test_final_scaled)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
mse_rf = mean_squared_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mse_rf)  # Исправление: вычисляем RMSE вручную
r2_rf = r2_score(y_test, y_pred_rf)

# Таблица сравнения
metrics_df = pd.DataFrame({
    'Model': ['Linear Regression', 'Random Forest'],
    'MAE': [mae_lr, mae_rf],
    'MSE': [mse_lr, mse_rf],
    'RMSE': [rmse_lr, rmse_rf],
    'R²': [r2_lr, r2_rf]
})
print("\n4.3 Сравнительная таблица метрик")
print(metrics_df)

### 5 Линейная регрессия
### 5.1 Базовая линейная регрессия
# Используем финальные данные
X = X_train_final_scaled.iloc[:, :2]
y = y_train
regression = LinearRegression()
model = regression.fit(X, y)

# Взглянуть на точку пересечения
print("\n5.1 Базовая линейная регрессия")
print("Точка пересечения (intercept):", model.intercept_)
print("Коэффициенты признаков (coef):", model.coef_)
print("Первое значение целевой переменной:", y.iloc[0])

# Предсказать целевое значение первого наблюдения, умноженное на 1000
prediction_first = model.predict(X.iloc[[0]])[0] * 1000
print("Предсказанное значение первого наблюдения (умноженное на 1000):", prediction_first)
print("Первый коэффициент (умноженный на 100_000):", model.coef_[0] * 100_000)

### 5.2 Учёт взаимодействий между признаками
# Используем первые два числовых признака из финальных данных
X = X_train_final_scaled.iloc[:, :2].values  # Преобразуем в numpy array
y = y_train

# Создать взаимодействующие признаки с помощью PolynomialFeatures
interaction = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
features_interaction = interaction.fit_transform(X)

# Обучить модель
regression = LinearRegression()
model = regression.fit(features_interaction, y)

# Посмотреть признаки первого наблюдения
print("\n5.2 Учёт взаимодействий между признаками")
print("Исходные признаки первого наблюдения:", X[0])
print("Признаки с взаимодействием первого наблюдения:", features_interaction[0])

interaction_term = np.multiply(X[:, 0], X[:, 1])
print("Взаимодействие первого наблюдения (ручной расчёт):", interaction_term[0])

def interaction_dance_energy(X):
    return (X[:, 0] * X[:, 1]).reshape(-1, 1)
# Создаём трансформер
interaction_transformer = FunctionTransformer(interaction_dance_energy, validate=False)
preprocessor = ColumnTransformer(
    transformers=[
        ("original", "passthrough", [0, 1]),
        ("interaction", interaction_transformer, [0, 1])
    ]
)

# Строим модель
pipeline = Pipeline([
    ("features", preprocessor),
    ("regression", LinearRegression())
])
pipeline.fit(X, y)

# Проверим первые признаки после трансформации
print("Признаки первого наблюдения после трансформации (Pipeline):", preprocessor.fit_transform(X)[:1])

### 5.3 Моделирование нелинейных зависимостей
# Используем один числовой признак из финальных данных (например, первый признак)
X = X_train_final_scaled.iloc[:, [0]].values  # Берем первый признак
y = y_train

# Полиномиальные признаки x^2 и x^3
polynomial = PolynomialFeatures(degree=3, include_bias=False)
features_polynomial = polynomial.fit_transform(X)
regression = LinearRegression()
model = regression.fit(features_polynomial, y)

# Взглянуть на первое наблюдение
print("\n5.3 Моделирование нелинейных зависимостей")
print("Первое наблюдение (x):", X[0, 0])
print("Первое наблюдение (x^2):", X[0, 0]**2)
print("Первое наблюдение (x^3):", X[0, 0]**3)
print("Значения первого наблюдения (x, x^2, x^3):", features_polynomial[0])

# Модель со сплайнами
spline_model = make_pipeline(
    SplineTransformer(degree=3, n_knots=5),
    LinearRegression()
)
spline_model.fit(X, y)

### 5.4 Снижение дисперсии с помощью регуляризации
# Используем финальные стандартизированные данные
X = X_train_final_scaled.values
y = y_train
regression = Ridge(alpha=0.5)

model = regression.fit(X, y)

# Создание объекта гребневой регрессии с тремя значениями alpha
regr_cv = RidgeCV(alphas=[0.1, 1.0, 10.0])
model_cv = regr_cv.fit(X, y)

# Взглянуть на коэффициенты
print("\n5.4 Снижение дисперсии с помощью регуляризации")
print("Коэффициенты модели с фиксированным alpha=0.5:", model.coef_[:5])
print("Коэффициенты модели с подобранным alpha:", model_cv.coef_[:5])

# Взглянуть на alpha
print("Подобранное значение alpha:", model_cv.alpha_)

### 5.5 Уменьшение количества признаков с помощью лассо-регрессии
# Используем финальные стандартизированные данные
X = X_train_final_scaled.values  # Преобразуем в numpy array
y = y_train

# Создать объект лассо-регрессии со значением alpha
regression = Lasso(alpha=0.01)

# Выполнить подгонку линейной регрессии
model = regression.fit(X, y)

# Взглянуть на коэффициенты
print("\n5.5 Уменьшение количества признаков с помощью лассо-регрессии")
print("Коэффициенты модели с alpha=0.01 (первые 10):", model.coef_[:10])

# Создать лассо-регрессию с высоким alpha
regression_a10 = Lasso(alpha=1)

# Выполнить подгонку линейной регрессии
model_a10 = regression_a10.fit(X, y)

# Взглянуть на коэффициенты
print("Коэффициенты модели с alpha=1 (первые 10):", model_a10.coef_[:10])

### 5.6 Эластичная сеть (Elastic Net)
# Используем финальные стандартизированные данные
X = X_train_final_scaled.values
y = y_train

# Пайплайн: стандартизация не требуется, так как данные уже стандартизированы
model = make_pipeline(
    ElasticNetCV(
        l1_ratio=[0.1, 0.5, 0.9],
        alphas=[0.001, 0.01, 0.1, 1.0],
        cv=5,
        random_state=42
    )
)

# Обучить модель
model.fit(X, y)

# Извлечь параметры эластичной сети
elastic = model.named_steps["elasticnetcv"]

print("\n5.6 Эластичная сеть (Elastic Net)")
print("Оптимальное значение alpha:", elastic.alpha_)
print("Оптимальное значение l1_ratio:", elastic.l1_ratio_)
print("Количество ненулевых коэффициентов:", np.sum(elastic.coef_ != 0))

### 5.7 Оценка на тестовом наборе
# Используем тестовые данные
X_test = X_test_final_scaled.values
y_test = y_test

# Предсказания с лучшей моделью из ElasticNetCV
y_pred = model.predict(X_test)

# Оценка метрик
mse_test = mean_squared_error(y_test, y_pred)
rmse_test = np.sqrt(mse_test)
r2_test = r2_score(y_test, y_pred)

print("\n5.7 Оценка на тестовом наборе")
print("Среднеквадратичная ошибка (MSE) на тесте:", mse_test)
print("RMSE на тесте:", rmse_test)
print("R² на тесте:", r2_test)

# Проверка совместимости признаков
print("Количество признаков в X_train_final_scaled:", X_train_final_scaled.shape[1])
print("Количество признаков в X_test_final_scaled:", X_test_final_scaled.shape[1])


### 5.8 Лучшая модель: Random Forest и XGBoost
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

# Числовые признаки для синхронизации
numeric_cols = X_train_final_scaled.select_dtypes(include=['int64', 'float64']).columns
X_train_scaled = X_train_final_scaled[numeric_cols]
X_test_scaled = X_test_final_scaled[numeric_cols]

# Тюнинг Random Forest
rf = RandomForestRegressor(random_state=42)
param_grid_rf = {
    'n_estimators': [100],
    'max_depth': [10, None],
    'min_samples_split': [2],
    'min_samples_leaf': [1]
}
grid_search_rf = GridSearchCV(rf, param_grid_rf, cv=5, scoring='r2', n_jobs=-1)
grid_search_rf.fit(X_train_scaled, y_train)
best_rf = grid_search_rf.best_estimator_
print(f"\n5.8 Лучшая модель: Random Forest")
print(f"Лучшие параметры RF: {grid_search_rf.best_params_}")
y_pred_rf = best_rf.predict(X_test_scaled)
r2_rf = r2_score(y_test, y_pred_rf)
print(f"R² Random Forest: {r2_rf:.4f}")

# XGBoost
xgb = XGBRegressor(random_state=42, n_jobs=-1)
param_grid_xgb = {
    'n_estimators': [100],
    'max_depth': [3, 6],
    'learning_rate': [0.1]
}
grid_search_xgb = GridSearchCV(xgb, param_grid_xgb, cv=5, scoring='r2', n_jobs=-1)
grid_search_xgb.fit(X_train_scaled, y_train)
best_xgb = grid_search_xgb.best_estimator_
print(f"Лучшие параметры XGBoost: {grid_search_xgb.best_params_}")
y_pred_xgb = best_xgb.predict(X_test_scaled)
r2_xgb = r2_score(y_test, y_pred_xgb)
print(f"R² XGBoost: {r2_xgb:.4f}")

# Ансамбль
ensemble = VotingRegressor(estimators=[('rf', best_rf), ('xgb', best_xgb)], weights=[0.5, 0.5])
ensemble.fit(X_train_scaled, y_train)
y_pred_ensemble = ensemble.predict(X_test_scaled)
r2_ensemble = r2_score(y_test, y_pred_ensemble)
print(f"\n5.9 Ансамбль моделей")
print(f"Итоговый R² ансамбля: {r2_ensemble:.4f}")

# Проверка переобучения
cv_scores_rf = cross_val_score(best_rf, X_train_scaled, y_train, cv=5, scoring='r2')
print(f"Средний R² кросс-валидации RF: {cv_scores_rf.mean():.4f} (+/- {cv_scores_rf.std() * 2:.4f})")
cv_scores_xgb = cross_val_score(best_xgb, X_train_scaled, y_train, cv=5, scoring='r2')
print(f"Средний R² кросс-валидации XGBoost: {cv_scores_xgb.mean():.4f} (+/- {cv_scores_xgb.std() * 2:.4f})")

# График предсказаний
best_model = 'Random Forest' if r2_rf > r2_xgb else 'XGBoost'
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred_rf if best_model == 'Random Forest' else y_pred_xgb, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Реальные значения')
plt.ylabel('Предсказанные значения')
plt.title(f'Сравнение предсказаний ({best_model})')
plt.show()

print("\nАнализ завершён успешно!")