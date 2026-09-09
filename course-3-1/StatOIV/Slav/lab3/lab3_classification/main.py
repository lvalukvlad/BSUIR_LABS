import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.utils import class_weight

### 1. Выбор датасета
# Загружаем датасет
df = pd.read_csv('train.csv')
# Проверяем размер и первые строки
print("Размер датасета:", df.shape)
print("\nПервые 5 строк:")
print(df.head())
# Получаем общую информацию о данных
print("\nИнформация о датасете:")
print(df.info())
# Проверяем наличие пропущенных значений
print("\nКоличество пропущенных значений по колонкам:")
print(df.isnull().sum())

### 2. Предобработка данных
### Анализ пропущенных значений и их обработка (удаление или заполнение)
# Процент пропущенных значений по каждой колонке
missing_percent = df.isnull().mean() * 100
print("\nПроцент пропущенных значений по колонкам:")
print(missing_percent[missing_percent > 0])
# Визуализация пропущенных значений
plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull(), cbar=True, cmap='viridis')
plt.title('Тепловая карта пропущенных значений')
plt.show()
# Обработка пропусков
# Для категориальных колонок заполняем 'None' или модой
categorical_cols_with_na = ['Alley', 'MasVnrType', 'BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2',
                            'Electrical', 'FireplaceQu', 'GarageType', 'GarageFinish', 'GarageQual', 'GarageCond',
                            'PoolQC', 'Fence', 'MiscFeature']
for col in categorical_cols_with_na:
    df[col] = df[col].fillna('None')
# Для числовых колонок заполняем средним или медианой
numeric_cols_with_na = ['LotFrontage', 'MasVnrArea', 'GarageYrBlt']
for col in numeric_cols_with_na:
    df[col] = df[col].fillna(df[col].median())
# Удаление колонок с большим количеством пропусков, если нужно (но здесь обработали)
# Проверка после обработки
print("\nКоличество пропущенных значений после обработки:")
print(df.isnull().sum())

### Обнаружение и обработка выбросов
# Выбор числовых колонок
numeric_cols = ['LotFrontage', 'LotArea', 'YearBuilt', 'MasVnrArea', 'BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF',
                'TotalBsmtSF', '1stFlrSF', '2ndFlrSF', 'GrLivArea', 'GarageYrBlt', 'GarageArea', 'WoodDeckSF',
                'OpenPorchSF', 'EnclosedPorch', 'ScreenPorch', 'SalePrice']
# Функция для обнаружения выбросов с помощью IQR
def detect_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
    return outliers
# Применяем для каждой числовой колонки
for col in numeric_cols:
    outliers = detect_outliers(df, col)
    print(f"\nВыбросы в {col}:")
    print(f"Количество выбросов: {len(outliers)}")
    print(f"Процент выбросов: {(len(outliers) / len(df)) * 100:.2f}%")
    print(f"Значения выбросов: {outliers.tolist()[:5]}...")
# Визуализация бокс-плотов для числовых колонок
plt.figure(figsize=(15, 10))
for i, col in enumerate(numeric_cols[:6], 1):
    plt.subplot(2, 3, i)
    sns.boxplot(y=df[col])
    plt.title(col)
plt.tight_layout()
plt.show()
# Функция для обрезки выбросов
def cap_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df[column] = df[column].clip(lower_bound, upper_bound)
    return df
# Применяем обрезку к колонкам с выбросами (например, LotArea, GrLivArea)
cols_to_cap = ['LotFrontage', 'LotArea', 'MasVnrArea', 'BsmtFinSF1', 'GrLivArea', 'GarageArea']
for col in cols_to_cap:
    df = cap_outliers(df, col)
# Проверка после обработки
print("\nСтатистика после обработки выбросов:")
for col in cols_to_cap:
    print(f"{col}: min={df[col].min():.2f}, max={df[col].max():.2f}")

### Кодирование категориальных переменных
# Определяем категориальные колонки
categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
# Проверяем уникальные значения для анализа
for col in categorical_cols[:5]:  # Первые 5 для примера
    print(f"\nУникальные значения в {col}:")
    print(df[col].unique())
# One-Hot Encoding для неупорядоченных переменных
one_hot_cols = categorical_cols
encoder_one_hot = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
encoded_one_hot = encoder_one_hot.fit_transform(df[one_hot_cols])
encoded_df_one_hot = pd.DataFrame(encoded_one_hot, columns=encoder_one_hot.get_feature_names_out(one_hot_cols))
# Объединяем закодированные данные с исходным датасетом (удаляем оригинальные категориальные)
df_encoded = pd.concat([df.drop(categorical_cols + ['Id'], axis=1), encoded_df_one_hot], axis=1)
# Проверяем результат
print("\nРазмер датасета после кодирования:", df_encoded.shape)
print("\nПервые 5 строк после кодирования:")
print(df_encoded.head())
print("\nИнформация о датасете после кодирования:")
print(df_encoded.info())
# Визуализация корреляции (маленький срез для скорости)
plt.figure(figsize=(12, 8))
sns.heatmap(df_encoded.iloc[:, :10].corr(), cmap='coolwarm', center=0)
plt.title('Корреляция признаков (срез)')
plt.show()

### Масштабирование числовых признаков
# Определяем числовые колонки (исключаем закодированные и целевую)
numeric_cols_all = [col for col in df_encoded.columns if col != 'SalePrice' and 'onehot' not in col.lower()]
print("\nЧисловые колонки для масштабирования:", numeric_cols_all)
# Инициализируем StandardScaler
scaler = StandardScaler()
df_encoded[numeric_cols_all] = scaler.fit_transform(df_encoded[numeric_cols_all])
# Проверка результата
print("\nСтатистика после масштабирования:")
print(df_encoded[numeric_cols_all].describe())
print("\nПервые 5 строк после масштабирования:")
print(df_encoded.head())
# Визуализация распределения до и после масштабирования (срез)
plt.figure(figsize=(15, 10))
for i, col in enumerate(numeric_cols_all[:3], 1):
    plt.subplot(2, 3, i)
    sns.histplot(df[col], kde=True, color='blue', label='До')
    sns.histplot(df_encoded[col], kde=True, color='red', label='После')
    plt.title(col)
    plt.legend()
plt.tight_layout()
plt.show()

### Адаптация к задаче классификации (преобразование SalePrice в бинарную категорию)
median_price = df_encoded['SalePrice'].median()
df_encoded['is_expensive'] = (df_encoded['SalePrice'] > median_price).astype(int)
# Удаляем оригинальную SalePrice
df_encoded = df_encoded.drop('SalePrice', axis=1)

### Разделение выборки на обучающую и тестовую
# Определяем признаки (X) и целевую переменную (y)
X = df_encoded.drop(['is_expensive'], axis=1)
y = df_encoded['is_expensive']
# Разделяем на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Проверяем размеры
print("\nРазмер обучающей выборки (X_train):", X_train.shape)
print("Размер тестовой выборки (X_test):", X_test.shape)
print("Размер обучающей выборки (y_train):", y_train.shape)
print("Размер тестовой выборки (y_test):", y_test.shape)
# Первые 5 строк обучающей выборки
print("\nПервые 5 строк X_train:")
print(X_train.head())
print("\nПервые 5 значений y_train:")
print(y_train.head())

### 3. Построение и обучение моделей
### 1) Дерево решений (DecisionTreeClassifier)
dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X_train, y_train)
# Предсказания
y_pred_dt = dt_model.predict(X_test)
# Оценка модели
accuracy_dt = accuracy_score(y_test, y_pred_dt)
precision_dt = precision_score(y_test, y_pred_dt)
recall_dt = recall_score(y_test, y_pred_dt)
f1_dt = f1_score(y_test, y_pred_dt)
y_pred_prob_dt = dt_model.predict_proba(X_test)[:, 1]
roc_auc_dt = roc_auc_score(y_test, y_pred_prob_dt)
# Вывод результатов
print("\nРезультаты DecisionTreeClassifier:")
print(f"Accuracy: {accuracy_dt:.2f}")
print(f"Precision: {precision_dt:.2f}")
print(f"Recall: {recall_dt:.2f}")
print(f"F1-Score: {f1_dt:.2f}")
print(f"ROC-AUC: {roc_auc_dt:.2f}")
# Визуализация важности признаков
importances = dt_model.feature_importances_
feature_names = X.columns
feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance_df.head(10))
plt.title('Топ-10 важных признаков (DecisionTree)')
plt.show()

### 2) k ближайших соседей (KNeighborsClassifier)
knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train, y_train)
# Предсказания
y_pred_knn = knn_model.predict(X_test)
# Оценка модели
accuracy_knn = accuracy_score(y_test, y_pred_knn)
precision_knn = precision_score(y_test, y_pred_knn)
recall_knn = recall_score(y_test, y_pred_knn)
f1_knn = f1_score(y_test, y_pred_knn)
y_pred_prob_knn = knn_model.predict_proba(X_test)[:, 1]
roc_auc_knn = roc_auc_score(y_test, y_pred_prob_knn)
# Вывод результатов
print("\nРезультаты KNeighborsClassifier:")
print(f"Accuracy: {accuracy_knn:.2f}")
print(f"Precision: {precision_knn:.2f}")
print(f"Recall: {recall_knn:.2f}")
print(f"F1-Score: {f1_knn:.2f}")
print(f"ROC-AUC: {roc_auc_knn:.2f}")

### 3) Логистическая регрессия (LogisticRegression)
lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train, y_train)
# Предсказания
y_pred_lr = lr_model.predict(X_test)
# Оценка модели
accuracy_lr = accuracy_score(y_test, y_pred_lr)
precision_lr = precision_score(y_test, y_pred_lr)
recall_lr = recall_score(y_test, y_pred_lr)
f1_lr = f1_score(y_test, y_pred_lr)
y_pred_prob_lr = lr_model.predict_proba(X_test)[:, 1]
roc_auc_lr = roc_auc_score(y_test, y_pred_prob_lr)
# Вывод результатов
print("\nРезультаты LogisticRegression:")
print(f"Accuracy: {accuracy_lr:.2f}")
print(f"Precision: {precision_lr:.2f}")
print(f"Recall: {recall_lr:.2f}")
print(f"F1-Score: {f1_lr:.2f}")
print(f"ROC-AUC: {roc_auc_lr:.2f}")

### 4) Наивный байесовский классификатор (GaussianNB)
nb_model = GaussianNB()
nb_model.fit(X_train, y_train)
# Предсказания
y_pred_nb = nb_model.predict(X_test)
# Оценка модели
accuracy_nb = accuracy_score(y_test, y_pred_nb)
precision_nb = precision_score(y_test, y_pred_nb)
recall_nb = recall_score(y_test, y_pred_nb)
f1_nb = f1_score(y_test, y_pred_nb)
y_pred_prob_nb = nb_model.predict_proba(X_test)[:, 1]
roc_auc_nb = roc_auc_score(y_test, y_pred_prob_nb)
print("\nРезультаты GaussianNB:")
print(f"Accuracy: {accuracy_nb:.2f}")
print(f"Precision: {precision_nb:.2f}")
print(f"Recall: {recall_nb:.2f}")
print(f"F1-Score: {f1_nb:.2f}")
print(f"ROC-AUC: {roc_auc_nb:.2f}")

### 4. Оценка качества моделей
metrics = {
    'DecisionTree': {
        'Accuracy': accuracy_score(y_test, y_pred_dt),
        'Precision': precision_score(y_test, y_pred_dt),
        'Recall': recall_score(y_test, y_pred_dt),
        'F1-Score': f1_score(y_test, y_pred_dt),
        'ROC-AUC': roc_auc_score(y_test, y_pred_prob_dt)
    },
    'KNeighbors': {
        'Accuracy': accuracy_score(y_test, y_pred_knn),
        'Precision': precision_score(y_test, y_pred_knn),
        'Recall': recall_score(y_test, y_pred_knn),
        'F1-Score': f1_score(y_test, y_pred_knn),
        'ROC-AUC': roc_auc_score(y_test, y_pred_prob_knn)
    },
    'LogisticRegression': {
        'Accuracy': accuracy_score(y_test, y_pred_lr),
        'Precision': precision_score(y_test, y_pred_lr),
        'Recall': recall_score(y_test, y_pred_lr),
        'F1-Score': f1_score(y_test, y_pred_lr),
        'ROC-AUC': roc_auc_score(y_test, y_pred_prob_lr)
    },
    'GaussianNB': {
        'Accuracy': accuracy_score(y_test, y_pred_nb),
        'Precision': precision_score(y_test, y_pred_nb),
        'Recall': recall_score(y_test, y_pred_nb),
        'F1-Score': f1_score(y_test, y_pred_nb),
        'ROC-AUC': roc_auc_score(y_test, y_pred_prob_nb)
    }
}
# Сравнительная таблица
metrics_df = pd.DataFrame(metrics).T
print("\nСравнительная таблица метрик:")
print(metrics_df.round(2))
# Confusion Matrix для каждой модели
models = {'DecisionTree': dt_model, 'KNeighbors': knn_model, 'LogisticRegression': lr_model, 'GaussianNB': nb_model}
plt.figure(figsize=(15, 10))
for i, (name, model) in enumerate(models.items(), 1):
    plt.subplot(2, 2, i)
    cm = confusion_matrix(y_test, model.predict(X_test))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.title(f'Confusion Matrix - {name}')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
plt.tight_layout()
plt.show()