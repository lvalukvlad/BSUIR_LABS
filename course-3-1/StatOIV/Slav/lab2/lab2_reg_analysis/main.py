import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, PolynomialFeatures, FunctionTransformer, OneHotEncoder
from sklearn.model_selection import KFold, train_test_split, cross_validate, cross_val_predict, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, SimpleImputer, IterativeImputer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNetCV, RidgeCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from xgboost import XGBRegressor
from scipy.stats import loguniform
import warnings
warnings.filterwarnings('ignore')

# Загрузка датасета
data_raw = pd.read_csv('train.csv')
print("Исходные данные:")
print(data_raw.info())
print(f"Размер: {data_raw.shape}")

# Отделим целевую переменную
y_raw = data_raw['SalePrice'].copy()
X_raw = data_raw.drop(['SalePrice', 'Id'], axis=1)

# Списки признаков
numeric_cols = X_raw.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = X_raw.select_dtypes(exclude=[np.number]).columns.tolist()

print("Числовые признаки:", len(numeric_cols))
print("Категориальные признаки:", len(categorical_cols))
print("Пропуски в числовых признаках:")
print(X_raw[numeric_cols].isnull().sum().sort_values(ascending=False).head(10))
print("Пропуски в категориальных признаках:")
print(X_raw[categorical_cols].isnull().sum().sort_values(ascending=False).head(10))

# Обработка пропусков в категориальных признаках (NA = отсутствие)
for col in categorical_cols:
    X_raw[col] = X_raw[col].fillna("None")

# Обработка пропусков в числовых признаках
X_raw['LotFrontage'] = X_raw.groupby('Neighborhood')['LotFrontage'].transform(
    lambda x: x.fillna(x.median())
)
X_raw[numeric_cols] = X_raw[numeric_cols].fillna(0)

# Инженерия признаков
X_raw['TotalSF'] = X_raw['TotalBsmtSF'] + X_raw['1stFlrSF'] + X_raw['2ndFlrSF']
X_raw['HouseAge'] = X_raw['YrSold'] - X_raw['YearBuilt']
X_raw['TotalBath'] = (X_raw['FullBath'] + 0.5 * X_raw['HalfBath'] +
                     X_raw['BsmtFullBath'] + 0.5 * X_raw['BsmtHalfBath'])
X_raw['HasPool'] = (X_raw['PoolArea'] > 0).astype(int)
X_raw['Has2ndFloor'] = (X_raw['2ndFlrSF'] > 0).astype(int)
X_raw['HasGarage'] = (X_raw['GarageArea'] > 0).astype(int)

# Логарифмирование целевой переменной для нормализации
y_log = np.log1p(y_raw)

# Обновим списки после создания новых признаков
numeric_cols = X_raw.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = X_raw.select_dtypes(exclude=[np.number]).columns.tolist()

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

# Разделение на обучающую и тестовую выборки
X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X_raw, y_log, test_size=0.2, random_state=42
)

# Кодирование категориальных признаков
encoder = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
encoded_cat_train = encoder.fit_transform(X_train_raw[categorical_cols])
encoded_cat_test = encoder.transform(X_test_raw[categorical_cols])

# Числовые признаки
num_train = X_train_raw[numeric_cols].values
num_test = X_test_raw[numeric_cols].values

# Объединение
X_train_combined = np.hstack([num_train, encoded_cat_train])
X_test_combined = np.hstack([num_test, encoded_cat_test])

# Стандартизация
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_combined)
X_test_scaled = scaler.transform(X_test_combined)

# Преобразуем обратно в DataFrame для удобства
feature_names = (numeric_cols +
                 encoder.get_feature_names_out(categorical_cols).tolist())
X_train_final = pd.DataFrame(X_train_scaled, columns=feature_names)
X_test_final = pd.DataFrame(X_test_scaled, columns=feature_names)

### 1.6 Обработка выбросов — визуализация
plt.figure(figsize=(10, 6))
sns.boxplot(x=data_raw['SalePrice'])
plt.title('Boxplot цены дома (до лог-трансформации)')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x=y_log)
plt.title('Boxplot логарифмированной цены (после трансформации)')
plt.show()

### 1.8 Удаление наблюдений с пропущенных значений
data_with_nans = data_raw.copy()
data_no_nans = data_with_nans.dropna()
print(f"Исходно: {len(data_with_nans)} строк, после удаления: {len(data_no_nans)} строк")

### 1.9 Заполнение пропущенных значений
# Создадим копию с пропусками
numeric_data = X_raw[numeric_cols].values
scaler_temp = StandardScaler()
standardized_numeric = scaler_temp.fit_transform(numeric_data)
# Внесём искусственный пропуск
standardized_numeric[0, 0] = np.nan
imputer = KNNImputer(n_neighbors=5)
numeric_imputed = imputer.fit_transform(standardized_numeric)
print("Истинное значение первого числового признака:", scaler_temp.inverse_transform(standardized_numeric)[0, 0])
print("Заполненное значение:", scaler_temp.inverse_transform(numeric_imputed)[0, 0])

### 2.1 Кодирование номинальных категориальных признаков
encoder_demo = OneHotEncoder(drop='first', sparse_output=False)
categorical_demo = X_raw[categorical_cols[:2]]  # только для демонстрации
encoded_demo = encoder_demo.fit_transform(categorical_demo)
print("Размер закодированных категориальных данных (пример):", encoded_demo.shape)

### 2.2 Кодирование порядковых категориальных признаков
from sklearn.preprocessing import OrdinalEncoder
# Например, OverallQual — уже порядковый, но в числах
# Возьмём, например, BsmtQual — категориальный с порядком
if 'BsmtQual' in X_raw.columns:
    ordinal_encoder = OrdinalEncoder(categories=[['None', 'Fa', 'TA', 'Gd', 'Ex']])
    X_raw['BsmtQual_ordinal'] = ordinal_encoder.fit_transform(X_raw[['BsmtQual']])
    print("Первые 5 значений BsmtQual_ordinal:")
    print(X_raw[['BsmtQual', 'BsmtQual_ordinal']].head())

### 2.3 Заполнение пропущенных значений в категориальных признаках
data_raw_filled = data_raw.copy()
imputer_freq = SimpleImputer(strategy="most_frequent")
data_raw_filled["Neighborhood"] = imputer_freq.fit_transform(data_raw[["Neighborhood"]])[:, 0]

imputer_const = SimpleImputer(strategy="constant", fill_value="missing")
data_raw_filled["Alley"] = imputer_const.fit_transform(data_raw[["Alley"]])[:, 0]

print("Пропуски после обработки Alley:", data_raw_filled["Alley"].isnull().sum())

### 3.1 Кросс-валидация моделей
pipeline = make_pipeline(StandardScaler(), LinearRegression())
cv = KFold(n_splits=5, shuffle=True, random_state=42)
cv_results = cross_validate(
    pipeline,
    X_train_final,
    y_train,
    cv=cv,
    scoring=['r2', 'neg_mean_squared_error'],
    n_jobs=-1
)
print("\n3.1 Кросс-валидация")
print("Средний R²:", cv_results['test_r2'].mean())
print("Средняя MSE:", -cv_results['test_neg_mean_squared_error'].mean())

### 3.2 Метрики регрессионных моделей
ols = LinearRegression()
predictions = cross_val_predict(ols, X_train_final, y_train, cv=5)
mse = mean_squared_error(y_train, predictions)
print("\n3.2 Метрики")
print("MSE:", mse)
r2_scores = cross_val_score(ols, X_train_final, y_train, scoring="r2", cv=5)
print("Средний R²:", r2_scores.mean())

### 3.3 RandomForestRegressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train_final, y_train)
y_pred_rf = rf_model.predict(X_test_final)

### 4.1 Отбор наилучших моделей с помощью исчерпывающего поиска (Ridge)
ridge = Ridge()
alpha = np.logspace(-3, 3, 20)
gridsearch = GridSearchCV(ridge, {'alpha': alpha}, cv=5, scoring='r2')
best_ridge = gridsearch.fit(X_train_final, y_train)
print("\n4.1 Лучший alpha (Ridge):", best_ridge.best_params_['alpha'])
print("Лучший R²:", best_ridge.best_score_)

### 4.2 Отбор наилучших моделей с помощью рандомизированного поиска (Lasso)
lasso = Lasso(max_iter=5000)
randomizedsearch = RandomizedSearchCV(
    lasso, {'alpha': loguniform(1e-4, 1e1)},
    n_iter=50, cv=5, scoring='r2', random_state=42, n_jobs=-1
)
best_lasso = randomizedsearch.fit(X_train_final, y_train)
print("\n4.2 Лучший alpha (Lasso):", best_lasso.best_params_['alpha'])
print("Лучший R²:", best_lasso.best_score_)

### 4.3 Полная оценка качества моделей
models = {
    'Linear Regression': LinearRegression(),
    'Ridge': best_ridge.best_estimator_,
    'Lasso': best_lasso.best_estimator_,
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
    'XGBoost': XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
}

metrics = []
for name, model in models.items():
    model.fit(X_train_final, y_train)
    y_pred = model.predict(X_test_final)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    metrics.append([name, mae, mse, rmse, r2])

metrics_df = pd.DataFrame(metrics, columns=['Model', 'MAE', 'MSE', 'RMSE', 'R²'])
print("\n4.3 Сравнительная таблица метрик")
print(metrics_df.to_string(index=False))

### 5.1 Базовая линейная регрессия
X_simple = X_train_final.iloc[:, :2]
regression = LinearRegression()
model = regression.fit(X_simple, y_train)
print("\n5.1 Базовая линейная регрессия")
print("Intercept:", model.intercept_)
print("Коэффициенты:", model.coef_)

### 5.2 Учёт взаимодействий между признаками
X = X_train_final.iloc[:, :2].values
interaction = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
X_inter = interaction.fit_transform(X)
model_inter = LinearRegression().fit(X_inter, y_train)
print("\n5.2 Признаки с взаимодействием (первое наблюдение):", X_inter[0])

### 5.3 Моделирование нелинейных зависимостей
X_nl = X_train_final.iloc[:, [0]].values
poly = PolynomialFeatures(degree=3, include_bias=False)
X_poly = poly.fit_transform(X_nl)
model_poly = LinearRegression().fit(X_poly, y_train)
print("\n5.3 Полиномиальные признаки (x, x², x³):", X_poly[0])

### 5.4 Снижение дисперсии с помощью регуляризации (RidgeCV)
regr_cv = RidgeCV(alphas=[0.1, 1.0, 10.0])
model_cv = regr_cv.fit(X_train_final, y_train)
print("\n5.4 Подобранное значение alpha (RidgeCV):", model_cv.alpha_)

### 5.5 Уменьшение количества признаков с помощью лассо-регрессии
lasso_model = Lasso(alpha=0.01, max_iter=5000).fit(X_train_final, y_train)
print("\n5.5 Ненулевые коэффициенты (Lasso, alpha=0.01):", np.sum(lasso_model.coef_ != 0))

### 5.6 Эластичная сеть (ElasticNetCV)
from sklearn.pipeline import Pipeline
elastic_pipe = Pipeline([
    ('elastic', ElasticNetCV(l1_ratio=[0.1, 0.5, 0.9], alphas=np.logspace(-4, 0, 20), cv=5, random_state=42))
])
elastic_pipe.fit(X_train_final, y_train)
elastic = elastic_pipe.named_steps['elastic']
print("\n5.6 ElasticNet")
print("Оптимальный alpha:", elastic.alpha_)
print("Оптимальный l1_ratio:", elastic.l1_ratio_)
print("Ненулевые коэффициенты:", np.sum(elastic.coef_ != 0))

### 5.7 Оценка на тестовом наборе (лучшая модель — ElasticNet)
y_pred_elastic = elastic_pipe.predict(X_test_final)
print("\n5.7 ElasticNet на тесте")
print("MSE:", mean_squared_error(y_test, y_pred_elastic))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred_elastic)))
print("R²:", r2_score(y_test, y_pred_elastic))

### 5.8 Лучшая модель: Random Forest и XGBoost
best_rf = RandomForestRegressor(n_estimators=100, max_depth=None, random_state=42)
best_xgb = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)

best_rf.fit(X_train_final, y_train)
best_xgb.fit(X_train_final, y_train)

y_pred_rf = best_rf.predict(X_test_final)
y_pred_xgb = best_xgb.predict(X_test_final)

r2_rf = r2_score(y_test, y_pred_rf)
r2_xgb = r2_score(y_test, y_pred_xgb)

print("\n5.8 Сравнение RF и XGBoost")
print(f"R² Random Forest: {r2_rf:.4f}")
print(f"R² XGBoost: {r2_xgb:.4f}")

# Ансамбль
ensemble = VotingRegressor([('rf', best_rf), ('xgb', best_xgb)], weights=[0.5, 0.5])
ensemble.fit(X_train_final, y_train)
y_pred_ens = ensemble.predict(X_test_final)
r2_ens = r2_score(y_test, y_pred_ens)

### Анализ важности признаков для лучшей модели
# Выбираем модель с наилучшим R² среди RF и XGBoost
if r2_rf >= r2_xgb:
    best_model_for_importance = best_rf
    model_name = "Random Forest"
else:
    best_model_for_importance = best_xgb
    model_name = "XGBoost"

# Получаем важность признаков
importances = best_model_for_importance.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': X_train_final.columns,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print(f"\nТоп-10 важных признаков ({model_name}):")
print(feature_importance_df.head(10))

# Визуализация
plt.figure(figsize=(10, 6))
sns.barplot(data=feature_importance_df.head(10), x='Importance', y='Feature')
plt.title(f'Важность признаков ({model_name})')
plt.xlabel('Важность')
plt.tight_layout()
plt.show()

print(f"\n5.9 R² ансамбля: {r2_ens:.4f}")

# Визуализация предсказаний
best_model_name = 'Random Forest' if r2_rf >= r2_xgb else 'XGBoost'
y_pred_best = y_pred_rf if r2_rf >= r2_xgb else y_pred_xgb

plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred_best, alpha=0.6, label=best_model_name)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Истинные значения (логарифм)')
plt.ylabel('Предсказанные значения')
plt.title(f'Сравнение предсказаний ({best_model_name})')
plt.legend()
plt.grid(True)
plt.show()

print("\nАнализ завершён успешно!")