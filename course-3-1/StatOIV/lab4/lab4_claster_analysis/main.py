import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score,
    normalized_mutual_info_score
)
from sklearn.neighbors import NearestNeighbors
from scipy.cluster.hierarchy import dendrogram, linkage
import warnings
warnings.filterwarnings('ignore')
from sklearn.manifold import TSNE

"""1. Выбор датасета"""
# 1.1 Загрузка датасета
print("1. Выбор датасета.")
# Загрузить CSV
df = pd.read_csv("gpu_1986-2026.csv")
print(f"Датасет загружен!")
print(f"Размер датасета: {df.shape[0]} строк, {df.shape[1]} столбцов")

# 1.2 Выбор целевой переменной для валидации
target_col = "Graphics Processor__Architecture"
print(f"Целевая переменная (для ARI/NMI): {target_col}")
print(f"Количество различных архитектур: {df[target_col].nunique()}")

# 1.3 Сохранение целевой переменной отдельно
true_labels_raw = df[target_col].copy()
print(f"Целевая переменная сохранена отдельно ({len(true_labels_raw)} значений)")

# 1.4 Исключение целевой переменной из датасета
# Работаем с данными как с неразмеченными
df_features = df.drop(columns=[target_col])
print(f"Целевая переменная исключена из признаков")
print(f"Размер данных без целевой переменной: {df_features.shape[0]} строк, {df_features.shape[1]} столбцов")

"""2. Предобработка данных"""

print("\n2. Предобработка данных.")
# Посмотрим, какие столбцы числовые
print("Поиск числовых признаков...")
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"Найдено {len(numeric_cols)} числовых столбцов.")

# Исключаем служебные и слишком разреженные столбцы
# Выбираем несколько разумных признаков
candidate_features = [
    "Render Config__Shading Units",
    "Render Config__Compute Units",
    "Render Config__TMUs",
    "Render Config__ROPs",
    "Render Config__L2 Cache",
    "Theoretical Performance__FP32 (float)",
]

# Проверяем, какие из них есть в датасете и числовые
features = [f for f in candidate_features if f in numeric_cols]

if len(features) == 0:
    print("Не найдено подходящих числовых признаков!")
    print("Доступные числовые столбцы:")
    print(numeric_cols[:20])
    exit(1)

print(f"\nВыбрано {len(features)} признаков для анализа:")
for f in features:
    print(f"   - {f}")

"""2.1. Анализ пропущенных значений и их обработка (удаление или заполнение)"""

print("\n2.1. Анализ пропущенных значений:")

# Оставляем только нужные признаки и целевую переменную
df_work = df[features + [target_col]].copy()

print("\nПропуски по выбранным признакам до удаления:")
print(df_work.isnull().sum())

# Подсчёт пропусков
missing_counts = df_work.isnull().sum()
missing_percent = (missing_counts / len(df_work)) * 100

print(f"\n{'Признак':<45} {'Пропусков':<12} {'Процент':<10}")
for col in features + [target_col]:
    count = missing_counts[col]
    pct = missing_percent[col]
    status = "❌" if count > 0 else "✅"
    print(f"{status} {col:<43} {count:<12} {pct:.2f}%")

total_missing = missing_counts.sum()
print(f"Итого пропусков: {total_missing}")

print("\nСтратегия обработки пропусков:")

# Анализируем процент пропусков
max_missing_pct = missing_percent[features].max()

if max_missing_pct < 5:
    strategy = "Удаление"
    print(f"   Пропусков мало (< 5%), применяем Удаление строк с NaN")
elif max_missing_pct < 30:
    strategy = "Удаление (можно рассмотреть заполнение)"
    print(f"   Пропусков умеренно ({max_missing_pct:.1f}%), применяем Удаление")
    print(f"       (альтернатива: заполнение средним/медианой)")
else:
    strategy = "Заполнение"
    print(f"   Пропусков много (> 30%), рекомендуется Заполнение средним/медианой")

print("\nПрименение стратегии:")

initial_rows = df_work.shape[0]

if "Удаление" in strategy:
    # Удаляем строки с любыми пропусками в выбранных признаках или целевой переменной
    df_work = df_work.dropna(subset=features + [target_col])
    removed_rows = initial_rows - df_work.shape[0]
    print(f"   Удалено строк с NaN: {removed_rows} из {initial_rows} ({removed_rows / initial_rows * 100:.2f}%)")
else:
    # Заполнение пропусков медианой (для числовых признаков)
    for feat in features:
        if df_work[feat].isnull().sum() > 0:
            median_value = df_work[feat].median()
            df_work[feat].fillna(median_value, inplace=True)
            print(f"   Заполнен признак '{feat}' медианой ({median_value:.2f})")

    # Для целевой переменной удаляем строки с пропусками
    df_work = df_work.dropna(subset=[target_col])
    removed_rows = initial_rows - df_work.shape[0]
    print(f"   Удалено строк с NaN в целевой переменной: {removed_rows}")

print(f"\nИтоговый размер после обработки: {df_work.shape[0]} строк")

# Проверка, что остались данные
if df_work.shape[0] == 0:
    print("Ошибка: Все строки были удалены! Выберите другие признаки или стратегию.")
    exit(1)

# Обновляем целевые метки для оставшихся строк
true_labels = df_work[target_col].values
le = LabelEncoder()
true_labels_encoded = le.fit_transform(true_labels)
print(f"Целевая переменная закодирована: {len(np.unique(true_labels_encoded))} классов")

# Матрица признаков
X = df_work[features].values
print(f"Матрица признаков: {X.shape[0]} объектов × {X.shape[1]} признаков")

"""2.2. Обнаружение и обработка выбросов (IQR)"""

print("\n2.2. Метод: IQR (Interquartile Range)")
print("   Выбросы определяются по правилу Тьюки:")
print("   Выброс, если: x < Q1 - 1.5×IQR  или  x > Q3 + 1.5×IQR")
print("   где IQR = Q3 - Q1 (межквартильный размах)")

print("\nОбнаружение выбросов (метод IQR) по каждому признаку:")

n_samples, n_features = X.shape
initial_size = n_samples

# Одномерная маска по объектам (не по признакам)
outliers_mask = np.ones(n_samples, dtype=bool)

for j in range(n_features):
    col = X[:, j]
    # Вычисляем квартили и IQR
    Q1 = np.percentile(col, 25)
    Q3 = np.percentile(col, 75)
    IQR = Q3 - Q1

    # Границы для выбросов
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Маска нормальных значений для этого признака
    mask = (col >= Q1 - 1.5 * IQR) & (col <= Q3 + 1.5 * IQR)
    outliers_in_feat = np.sum(~mask)

    if outliers_in_feat > 0:
        print(f"   {features[j]}:")
        print(f"      Границы: [{lower_bound:.2f}, {upper_bound:.2f}]")
        print(f"      Выбросы: {outliers_in_feat} ({outliers_in_feat / n_samples * 100:.1f}%)")
    else:
        print(f"   {features[j]}: выбросов не обнаружено")
    # Накапливаем маску: объект должен не быть выбросом по всем признакам
    outliers_mask = outliers_mask & mask

# Применение фильтрации

print("\nПрименение фильтрации:")

# Применяем маску к матрице признаков и целевым меткам
X = X[outliers_mask]
true_labels_encoded = true_labels_encoded[outliers_mask]

removed_outliers = initial_size - X.shape[0]
print(f"   Удалено выбросов: {removed_outliers} из {initial_size} ({removed_outliers/initial_size*100:.1f}%)")
print(f"   Оставшийся размер: {X.shape[0]} объектов × {X.shape[1]} признаков")

# Проверка, что остались данные
if X.shape[0] == 0:
    print("\nОшибка: Все объекты были удалены как выбросы!")
    print("   Рекомендация: ослабьте критерий (например, используйте 2×IQR или 3×IQR)")
    exit(1)

"""2.3. Кодирование категориальных признаков"""

print("\n2.3. Кодирование категориальных признаков:")

# Проверяем наличие категориальных признаков в выбранных для анализа
categorical_features = df_work[features].select_dtypes(include=['object', 'category']).columns.tolist()

if len(categorical_features) > 0:
    print(f"\nНайдено {len(categorical_features)} категориальных признаков:")
    for feat in categorical_features:
        print(f"   - {feat}")

    print("\nПрименяем One-Hot Encoding...")

    # One-Hot Encoding для категориальных признаков
    df_encoded = pd.get_dummies(df_work[features], columns=categorical_features, drop_first=True)

    # Обновляем список признаков и матрицу X
    features = df_encoded.columns.tolist()
    X = df_encoded.values

    print(f"После кодирования: {X.shape[1]} признаков (включая закодированные)")
else:
    print("Категориальных признаков не обнаружено.")
    print("   Все выбранные признаки имеют числовой тип.")
    print("   Кодирование не требуется.")

print(f"\nИтоговая матрица признаков: {X.shape[0]} объектов × {X.shape[1]} признаков")

"""2.4. Масштабирование числовых признаков"""

print("\n2.4. Масштабирование числовых признаков:")

print("\nСтатистика признаков до масштабирования:")
print(f"   Среднее значение по признакам: {X.mean(axis=0)}")
print(f"   Стандартное отклонение: {X.std(axis=0)}")
print(f"   Минимальные значения: {X.min(axis=0)}")
print(f"   Максимальные значения: {X.max(axis=0)}")

print("\nВыбор метода масштабирования:")
print("   Рассмотрены два метода:")
print("   - StandardScaler — приводит к среднему=0, стандартное отклонение=1 (подходит для K-Means, DBSCAN)")
print("   - MinMaxScaler — масштабирует в диапазон [0, 1] (чувствителен к выбросам)")

print("\nПрименяем StandardScaler:")

# Применяем StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("\nМасштабирование завершено!")

print("\nСтатистика признаков после масштабирования:")
print(f"   Среднее значение: {X_scaled.mean(axis=0).round(4)}")
print(f"   Стандартное отклонение: {X_scaled.std(axis=0).round(4)}")
print(f"   Минимальные значения: {X_scaled.min(axis=0).round(4)}")
print(f"   Максимальные значения: {X_scaled.max(axis=0).round(4)}")

print(f"\nИтоговая матрица для кластеризации: {X_scaled.shape[0]} объектов × {X_scaled.shape[1]} признаков")


"""\n3. Построение и обучение моделей кластеризации: KMeans"""

print("3. Построение и обучение моделей кластеризации: KMeans")
print("\nАлгоритм K-Means:")
print("   - Метод: разбиение на k кластеров с минимизацией внутрикластерной дисперсии")
print("   - Основан на евклидовом расстоянии")
print("   - Требует предварительного выбора числа кластеров k")

# 3.1. Подбор оптимального числа кластеров

print("\n3.1. Подбор оптимального числа кластеров k:")

k_range = range(2, 11)
inertias = []
silhouette_scores = []

print("\nПеребор значений k от 2 до 10:")
for k in k_range:
    kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans_temp.fit(X_scaled)
    labels_temp = kmeans_temp.labels_
    inertia = kmeans_temp.inertia_
    sil = silhouette_score(X_scaled, labels_temp)

    inertias.append(inertia)
    silhouette_scores.append(sil)

    print(f"   k={k}: inertia={inertia:.0f}, silhouette={sil:.4f}")

print("\nПостроение графиков для выбора k:")

plt.figure(figsize=(12, 5))

# График 1: Метод локтя
plt.subplot(1, 2, 1)
plt.plot(k_range, inertias, "bo-", linewidth=2, markersize=8)
plt.xlabel("Число кластеров (k)", fontsize=11)
plt.ylabel("Inertia (WCSS)", fontsize=11)
plt.title("Метод локтя для K-Means", fontsize=12, fontweight='bold')
plt.grid(True, alpha=0.3)

# График 2: Силуэтный анализ
plt.subplot(1, 2, 2)
plt.plot(k_range, silhouette_scores, "ro-", linewidth=2, markersize=8)
plt.xlabel("Число кластеров (k)", fontsize=11)
plt.ylabel("Silhouette Score", fontsize=11)
plt.title("Силуэтный анализ для K-Means", fontsize=12, fontweight='bold')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("kmeans_elbow_silhouette.png", dpi=300, bbox_inches="tight")
plt.close()
print("Сохранён график: kmeans_elbow_silhouette.png")

print("\nАнализ результатов:")

# Выбор k по максимуму Silhouette
optimal_k = k_range[np.argmax(silhouette_scores)]
max_silhouette = max(silhouette_scores)

print(f"   Метод локтя:")
print(f"      - Inertia монотонно убывает с ростом k")
print(f"      - Визуально «локоть» наблюдается при k ≈ {optimal_k}")

print(f"   Силуэтный анализ:")
print(f"      - Максимальный Silhouette Score = {max_silhouette:.4f} при k = {optimal_k}")
print(f"      - Высокое значение (> 0.5) указывает на хорошее разделение кластеров")

print(f"\nВыбранное оптимальное число кластеров: k = {optimal_k}")
print(f"   (на основе максимума Silhouette Score)")

print("\n3.2. Обучение финальной модели K-Means:")

kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(X_scaled)

print(f"Модель обучена с параметрами:")
print(f"   - n_clusters = {optimal_k}")
print(f"   - random_state = 42")
print(f"   - n_init = 10 (количество инициализаций)")

# Подсчёт размеров кластеров
unique, counts = np.unique(kmeans_labels, return_counts=True)
print(f"\nРазмеры кластеров:")
for cluster_id, count in zip(unique, counts):
    pct = count / len(kmeans_labels) * 100
    print(f"   Кластер {cluster_id}: {count} объектов ({pct:.1f}%)")

# Метрики качества
kmeans_sil = silhouette_score(X_scaled, kmeans_labels)
kmeans_db = davies_bouldin_score(X_scaled, kmeans_labels)
kmeans_ch = calinski_harabasz_score(X_scaled, kmeans_labels)
kmeans_ari = adjusted_rand_score(true_labels_encoded, kmeans_labels)
kmeans_nmi = normalized_mutual_info_score(true_labels_encoded, kmeans_labels)

print("\nМетрики качества:")
print(f"   Внутренние метрики (без использования истинных меток):")
print(f"      - Silhouette Score:       {kmeans_sil:.4f} (чем выше, тем лучше; диапазон [-1, 1])")
print(f"      - Davies–Bouldin Index:   {kmeans_db:.4f} (чем ниже, тем лучше)")
print(f"      - Calinski–Harabasz Index:{kmeans_ch:.2f} (чем выше, тем лучше)")

print(f"\n   Внешние метрики (с использованием истинных меток):")
print(f"      - Adjusted Rand Index (ARI): {kmeans_ari:.4f} (диапазон [-1, 1], 1 = идеальное совпадение)")
print(f"      - Normalized Mutual Info (NMI): {kmeans_nmi:.4f} (диапазон [0, 1], 1 = идеальное совпадение)")

"""3.3. Agglomerative Clustering (Агломеративная кластеризация)"""

print("\n3.3. Агломеративная кластеризация")

print("\nАлгоритм Agglomerative Clustering:")
print("   - Метод: иерархическая кластеризация (снизу вверх)")
print("   - Каждый объект начинает как отдельный кластер")
print("   - Итеративно объединяются ближайшие кластеры")
print("   - Требует выбора метода связи (linkage) и числа кластеров")

# 3.4. Выбор метода связи

print("\n3.4. Выбор метода связи (linkage):")

print("\nДоступные методы связи:")
print("   - ward — минимизирует внутрикластерную дисперсию (подходит для компактных кластеров)")
print("   - complete — максимальное расстояние между кластерами")
print("   - average — среднее расстояние между всеми парами точек")
print("   - single — минимальное расстояние между кластерами")

print("\nВыбранный метод: ward")
print("   Обоснование:")
print("   - Метод ward минимизирует дисперсию внутри кластеров")
print("   - Хорошо работает с евклидовым расстоянием (используется в K-Means)")
print("   - Подходит для данных после StandardScaler")
print("   - Формирует компактные, сферические кластеры")

print("\nПостроение дендрограммы:")

# Дендрограмма на подвыборке
sample_size = min(500, X_scaled.shape[0])
sample_idx = np.random.choice(X_scaled.shape[0], size=sample_size, replace=False)
X_sample = X_scaled[sample_idx]

print(f"Используется подвыборка из {sample_size} объектов для визуализации")

linkage_matrix = linkage(X_sample, method="ward")

plt.figure(figsize=(16, 7))
dendrogram(linkage_matrix,
           truncate_mode='lastp',  # Показывать только последние p объединений
           p=30,  # Количество отображаемых узлов
           leaf_rotation=90,
           leaf_font_size=10)
plt.title("Дендрограмма (метод Ward)", fontsize=14, fontweight='bold')
plt.xlabel("Индекс образца или размер кластера", fontsize=12)
plt.ylabel("Расстояние (Ward)", fontsize=12)
plt.axhline(y=10, color='r', linestyle='--', linewidth=2, label='Линия отсечения (k=2)')
plt.legend()
plt.tight_layout()
plt.savefig("dendrogram.png", dpi=300, bbox_inches="tight")
plt.close()
print("Сохранён график: dendrogram.png")

# 3.5. Определение числа кластеров по дендрограмме

print("\n3.5. Определение числа кластеров по дендрограмме:")

print("\nАнализ дендрограммы:")
print("   - Дендрограмма показывает процесс объединения кластеров")
print("   - Оптимальное k определяется по наибольшему вертикальному расстоянию")
print("   - Визуально наблюдается чёткое разделение на 2 больших кластера")

# Можно также сравнить с K-Means
n_clusters_agg = optimal_k  # Берём из K-Means для согласованности
print(f"\nВыбранное число кластеров: k = {n_clusters_agg}")

# 3.6. Обучение модели

print("\n3.6. Обучение модели Agglomerative Clustering:")

agg = AgglomerativeClustering(n_clusters=n_clusters_agg, linkage="ward")
agg_labels = agg.fit_predict(X_scaled)

print(f"Модель обучена с параметрами:")
print(f"   - n_clusters = {n_clusters_agg}")
print(f"   - linkage = 'ward'")
print(f"   - affinity = 'euclidean' (по умолчанию)")

# Подсчёт размеров кластеров
unique, counts = np.unique(agg_labels, return_counts=True)
print(f"\nРазмеры кластеров:")
for cluster_id, count in zip(unique, counts):
    pct = count / len(agg_labels) * 100
    print(f"   Кластер {cluster_id}: {count} объектов ({pct:.1f}%)")

# Оценка качества
agg_sil = silhouette_score(X_scaled, agg_labels)
agg_db = davies_bouldin_score(X_scaled, agg_labels)
agg_ch = calinski_harabasz_score(X_scaled, agg_labels)
agg_ari = adjusted_rand_score(true_labels_encoded, agg_labels)
agg_nmi = normalized_mutual_info_score(true_labels_encoded, agg_labels)

print("\nМетрики качества:")
print(f"   Внутренние метрики:")
print(f"      - Silhouette Score:       {agg_sil:.4f}")
print(f"      - Davies–Bouldin Index:   {agg_db:.4f}")
print(f"      - Calinski–Harabasz Index:{agg_ch:.2f}")

print(f"\n   Внешние метрики:")
print(f"      - Adjusted Rand Index (ARI): {agg_ari:.4f}")
print(f"      - Normalized Mutual Info (NMI): {agg_nmi:.4f}")


"""3.7. DBSCAN (Density-Based Spatial Clustering)"""

print("\n3.7. DBSCAN (Density-Based Spatial Clustering)")

print("\nАлгоритм DBSCAN:")
print("   - Метод: кластеризация на основе плотности")
print("   - Не требует заранее задавать число кластеров")
print("   - Автоматически выявляет выбросы (шум)")
print("   - Может находить кластеры произвольной формы")
print("   - Требует подбора двух параметров: eps и min_samples")

print("\nПараметры DBSCAN:")
print("   - eps — радиус окрестности точки (максимальное расстояние)")
print("   - min_samples — минимальное число точек для формирования кластера")

"""3.8.1. Построение k-distance graph для оценки eps"""

print("\n3.8.1. Построение k-distance graph для оценки eps:")

# Выбор k (обычно k = размерность данных или 4-5)
k_nn = X_scaled.shape[1]  # 4 признака
print(f"Выбрано k = {k_nn} (равно числу признаков)")
print("Общая рекомендация: k = min_samples или k = размерность данных")

# Вычисление расстояний до k-го ближайшего соседа
neighbors = NearestNeighbors(n_neighbors=k_nn)
neighbors_fit = neighbors.fit(X_scaled)
distances, indices = neighbors_fit.kneighbors(X_scaled)

# Берём расстояние до k-го соседа (последний столбец)
distances_k = np.sort(distances[:, -1])

# Построение графика
plt.figure(figsize=(12, 6))
plt.plot(distances_k, linewidth=1.5, color='blue')
plt.xlabel("Индекс точки (отсортировано по расстоянию)", fontsize=11)
plt.ylabel(f"{k_nn}-ближайшее расстояние", fontsize=11)
plt.title("K-distance график для определения eps", fontsize=13, fontweight='bold')
plt.grid(True, alpha=0.3)

# Добавляем горизонтальные линии для кандидатов eps
eps_95 = np.percentile(distances_k, 95)
eps_98 = np.percentile(distances_k, 98)
plt.axhline(y=eps_95, color='orange', linestyle='--', linewidth=1.5,
            label=f'95-й процентиль: {eps_95:.4f}')
plt.axhline(y=eps_98, color='red', linestyle='--', linewidth=1.5,
            label=f'98-й процентиль: {eps_98:.4f}')
plt.legend()

plt.tight_layout()
plt.savefig("k_distance_graph.png", dpi=300, bbox_inches="tight")
plt.close()
print("Сохранён график: k_distance_graph.png")

print("\nИнтерпретация k-distance graph:")
print("   - График показывает расстояние до k-го соседа для каждой точки")
print("   - Оптимальный eps находится в точке «локтя» (резкого изгиба)")
print("   - Точки после «локтя» — потенциальные выбросы")

"""3.8.2. Подбор параметров"""

print("\n3.8.2. Подбор параметров eps и min_samples:")

# Кандидаты для eps (процентили и статистические меры)
eps_candidates = [
    np.percentile(distances_k, 95),
    np.percentile(distances_k, 98),
    np.percentile(distances_k, 99),
    np.mean(distances_k) + np.std(distances_k),
]

print("Кандидаты для eps:")
for i, candidate in enumerate(eps_candidates, 1):
    print(f"   {i}. {candidate:.4f}")

# Выбираем первое положительное значение
eps_value = None
for candidate in eps_candidates:
    if candidate > 0:
        eps_value = candidate
        break

# Защита от нулевого eps
if eps_value is None or eps_value <= 0:
    eps_value = max(distances_k[-1], 0.1)
    print(f"Все кандидаты ≤ 0, используется резервное значение: {eps_value:.4f}")

# Выбор min_samples (обычно k+1 или больше)
min_samples_value = max(k_nn, 5)

print(f"\nВыбранные параметры:")
print(f"   eps = {eps_value:.4f}")
print(f"      (выбран 95-й процентиль k-расстояний)")
print(f"   min_samples = {min_samples_value}")
print(f"      (рекомендация: ≥ k+1 или ≥ размерность данных)")

"""3.9. Обучение модели DBSCAN"""

print("\n3.9. Обучение модели DBSCAN:")

dbscan = DBSCAN(eps=eps_value, min_samples=min_samples_value)
dbscan_labels = dbscan.fit_predict(X_scaled)

print(f" Модель обучена с параметрами:")
print(f"   - eps = {eps_value:.4f}")
print(f"   - min_samples = {min_samples_value}")
print(f"   - metric = 'euclidean' (по умолчанию)")

print("\nАнализ выбросов и метрик DBSCAN:")

# 1. Количество выбросов
n_outliers = np.sum(dbscan_labels == -1)
outlier_pct = n_outliers / len(dbscan_labels) * 100
print(f"Число выбросов (-1): {n_outliers} из {len(dbscan_labels)} ({outlier_pct:.2f}%)")

# 2. Проверка, если выбросов >20%
if outlier_pct > 20:
    print(f"Выбросы > 20%. Рекомендуется скорректировать параметры eps/min_samples!")
else:
    print(f"Процент выбросов допустим")

# 3. Количество кластеров (без учёта -1)
n_clusters_db = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
print(f"Число найденных кластеров: {n_clusters_db}")

# 4. Отбор не-выбросов для метрик
mask_core = dbscan_labels != -1
if np.sum(mask_core) > 0 and n_clusters_db > 1:
    db_sil = silhouette_score(X_scaled[mask_core], dbscan_labels[mask_core])
    db_db = davies_bouldin_score(X_scaled[mask_core], dbscan_labels[mask_core])
    db_ch = calinski_harabasz_score(X_scaled[mask_core], dbscan_labels[mask_core])
    db_ari = adjusted_rand_score(true_labels_encoded[mask_core], dbscan_labels[mask_core])
    db_nmi = normalized_mutual_info_score(true_labels_encoded[mask_core], dbscan_labels[mask_core])
    print("\nМетрики DBSCAN (без выбросов):")
    print(f"   Silhouette Score:         {db_sil:.4f}")
    print(f"   Davies–Bouldin Index:     {db_db:.4f}")
    print(f"   Calinski–Harabasz Index:  {db_ch:.2f}")
    print(f"   Adjusted Rand Index (ARI):{db_ari:.4f}")
    print(f"   Normalized Mutual Info:   {db_nmi:.4f}")
else:
    db_sil = db_db = db_ch = db_ari = db_nmi = np.nan
    print("  Недостаточно кластеров/точек для оценки метрик. Измени параметры DBSCAN!")

# Анализ результатов
print("\nАнализ результатов кластеризации:")

# Подсчёт кластеров и выбросов
n_outliers = np.sum(dbscan_labels == -1)
outlier_pct = n_outliers / len(dbscan_labels) * 100
n_clusters_db = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)

print(f"\nОбщая статистика:")
print(f"   Число найденных кластеров: {n_clusters_db}")
print(f"   Выбросов (шум, label=-1): {n_outliers} ({outlier_pct:.2f}%)")

# Проверка на большое количество выбросов
if outlier_pct > 20:
    print(f"\n  ВНИМАНИЕ: Выбросов больше 20%!")
    print(f"   Рекомендации:")
    print(f"      - Увеличить eps (например, до {eps_value * 1.5:.4f})")
    print(f"      - Уменьшить min_samples (например, до {max(3, min_samples_value - 2)})")
    print(f"      - Проверить качество предобработки данных")

# Размеры кластеров
if n_clusters_db > 0:
    unique, counts = np.unique(dbscan_labels[dbscan_labels != -1], return_counts=True)
    print(f"\n Размеры кластеров:")
    for cluster_id, count in zip(unique, counts):
        pct = count / len(dbscan_labels) * 100
        print(f"   Кластер {cluster_id}: {count} объектов ({pct:.1f}%)")

# Метрики только для точек не-выбросов
if n_clusters_db > 1:
    mask_core = dbscan_labels != -1
    n_core_points = np.sum(mask_core)

    if n_core_points > 0 and len(np.unique(dbscan_labels[mask_core])) > 1:
        print(f"Метрики рассчитаны для {n_core_points} точек (без выбросов).")

        db_sil = silhouette_score(X_scaled[mask_core], dbscan_labels[mask_core])
        db_db = davies_bouldin_score(X_scaled[mask_core], dbscan_labels[mask_core])
        db_ch = calinski_harabasz_score(X_scaled[mask_core], dbscan_labels[mask_core])
        db_ari = adjusted_rand_score(true_labels_encoded[mask_core], dbscan_labels[mask_core])
        db_nmi = normalized_mutual_info_score(true_labels_encoded[mask_core], dbscan_labels[mask_core])

        print("\nМетрики качества:")
        print(f"   Внутренние метрики:")
        print(f"      - Silhouette Score:       {db_sil:.4f}")
        print(f"      - Davies–Bouldin Index:   {db_db:.4f}")
        print(f"      - Calinski–Harabasz Index:{db_ch:.2f}")

        print(f"\n   Внешние метрики:")
        print(f"      - Adjusted Rand Index (ARI): {db_ari:.4f}")
        print(f"      - Normalized Mutual Info (NMI): {db_nmi:.4f}")
    else:
        db_sil = db_db = db_ch = db_ari = db_nmi = np.nan
        print("\n  Недостаточно кластеров для расчёта метрик")
        print("   Рекомендация: настройте параметры eps и min_samples")
else:
    db_sil = db_db = db_ch = db_ari = db_nmi = np.nan
    print("\n  DBSCAN не выделил кластеры (все точки — выбросы или 1 кластер)")
    print("   Рекомендация: увеличьте eps или уменьшите min_samples")

"""4. Оценка качества кластеризации"""

print("\n4. Оценка качества кластеризации")

"""4.1. Описание метрик"""

print("4.1. Используемые метрики оценки качества:")

print("Внутренние метрики:")

print("   1. Silhouette Score (коэффициент силуэта)")
print("      - Оценивает, насколько объект похож на свой кластер vs соседние кластеры")
print("      - Формула: s = (b - a) / max(a, b)")
print("        где a — среднее расстояние до точек своего кластера")
print("            b — среднее расстояние до точек ближайшего соседнего кластера")
print("      - Диапазон: [-1, 1]")
print("        > 0.7  — отличное разделение кластеров")
print("        > 0.5  — хорошее разделение")
print("        > 0.25 — приемлемое разделение")
print("        < 0.25 — плохое разделение, возможно перекрытие кластеров")
print("      - Чем выше → тем лучше")

print("\n   2. Davies–Bouldin Index (индекс Дэвиса–Боулдина)")
print("      - Оценивает отношение внутрикластерного расстояния к межкластерному")
print("      - Формула: DB = (1/k) * Σ max((σᵢ + σⱼ) / d(cᵢ, cⱼ))")
print("        где σᵢ — средний радиус кластера i")
print("            d(cᵢ, cⱼ) — расстояние между центроидами кластеров i и j")
print("      - Диапазон: [0, +∞]")
print("        < 1.0 — хорошее разделение")
print("        ≈ 1.0 — удовлетворительное")
print("        > 2.0 — плохое разделение")
print("      - Чем ниже → тем лучше")

print("\n   3. Calinski–Harabasz Index (индекс Калински–Харабаша)")
print("      - Оценивает отношение межкластерной дисперсии к внутрикластерной")
print("      - Также называется Variance Ratio Criterion")
print("      - Формула: CH = (SSB / (k-1)) / (SSW / (n-k))")
print("        где SSB — межкластерная сумма квадратов")
print("            SSW — внутрикластерная сумма квадратов")
print("            k — число кластеров, n — число объектов")
print("      - Диапазон: [0, +∞]")
print("        Высокое значение — компактные и хорошо разделённые кластеры")
print("      - Чем выше → тем лучше")

print("\nВнешние метрики (с использованием истинных меток):")

print("\n   4. Adjusted Rand Index (ARI)")
print("      - Оценивает согласованность кластеризации с истинными метками")
print("      - Диапазон: [-1, 1], где 1 = идеальное совпадение, 0 = случайное")

print("\n   5. Normalized Mutual Information (NMI)")
print("      - Оценивает информационную общность между кластерами и истинными метками")
print("      - Диапазон: [0, 1], где 1 = идеальное совпадение")

# Сводна таблица метрик
print("\nСводная таблица метрик для всех алгоритмов")

results = pd.DataFrame({
    "Алгоритм": ["K-Means", "Agglomerative", "DBSCAN"],
    "Кластеров": [optimal_k, n_clusters_agg, n_clusters_db],
    "Silhouette": [kmeans_sil, agg_sil, db_sil],
    "Davies-Bouldin": [kmeans_db, agg_db, db_db],
    "Calinski-Harabasz": [kmeans_ch, agg_ch, db_ch],
    "ARI": [kmeans_ari, agg_ari, db_ari],
    "NMI": [kmeans_nmi, agg_nmi, db_nmi],
})

print("\n", results.to_string(index=False))
results.to_csv("clustering_results.csv", index=False, encoding="utf-8-sig")
print("\nТаблица сохранена в файл: clustering_results.csv")

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

algs = ["K-Means", "Agglomerative", "DBSCAN"]
colors = ['#3498db', '#e74c3c', '#2ecc71']  # синий, красный, зелёный

# График 1: Silhouette Score (↑ лучше)
sil_values = [kmeans_sil, agg_sil, db_sil]
bars1 = axes[0].bar(algs, sil_values, color=colors, alpha=0.8, edgecolor='black')
axes[0].set_title('Silhouette Score\n(↑ выше = лучше)', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Значение', fontsize=11)
axes[0].set_ylim(0, 1)
axes[0].axhline(y=0.5, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Порог: 0.5')
axes[0].grid(axis='y', alpha=0.3)
axes[0].legend()
# Подписи значений на столбцах
for bar, val in zip(bars1, sil_values):
    if not np.isnan(val):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                     f'{val:.3f}', ha='center', fontsize=10, fontweight='bold')

# График 2: Davies-Bouldin Index (↓ ниже = лучше)
db_values = [kmeans_db, agg_db, db_db]
db_values_plot = [v if not np.isnan(v) else 0 for v in db_values]
bars2 = axes[1].bar(algs, db_values_plot, color=colors, alpha=0.8, edgecolor='black')
axes[1].set_title('Davies-Bouldin Index\n(↓ ниже = лучше)', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Значение', fontsize=11)
axes[1].axhline(y=1.0, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Порог: 1.0')
axes[1].grid(axis='y', alpha=0.3)
axes[1].legend()
for bar, val in zip(bars2, db_values):
    if not np.isnan(val):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     f'{val:.3f}', ha='center', fontsize=10, fontweight='bold')

# График 3: Calinski-Harabasz Index (↑ выше = лучше)
ch_values = [kmeans_ch, agg_ch, db_ch]
ch_values_plot = [v if not np.isnan(v) else 0 for v in ch_values]
bars3 = axes[2].bar(algs, ch_values_plot, color=colors, alpha=0.8, edgecolor='black')
axes[2].set_title('Calinski-Harabasz Index\n(↑ выше = лучше)', fontsize=12, fontweight='bold')
axes[2].set_ylabel('Значение', fontsize=11)
axes[2].grid(axis='y', alpha=0.3)
for bar, val in zip(bars3, ch_values):
    if not np.isnan(val):
        axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                     f'{val:.0f}', ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig("metrics_comparison.png", dpi=300, bbox_inches='tight')
plt.close()
print("Сохранён график: metrics_comparison.png")

# Рейтинг алгоритмов
print("\nРейтинг алгоритмов по метрикам")

print("\n Рейтинг по Silhouette Score (↑ выше = лучше):")
sil_ranking = sorted(zip(algs, sil_values), key=lambda x: x[1] if not np.isnan(x[1]) else -1, reverse=True)
for i, (alg, score) in enumerate(sil_ranking, 1):
    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
    if not np.isnan(score):
        print(f"   {medal} {i}. {alg:<15} {score:.4f}")

print("\n Рейтинг по Davies-Bouldin Index (↓ ниже = лучше):")
db_ranking = sorted(zip(algs, db_values), key=lambda x: x[1] if not np.isnan(x[1]) else float('inf'))
for i, (alg, score) in enumerate(db_ranking, 1):
    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
    if not np.isnan(score):
        print(f"   {medal} {i}. {alg:<15} {score:.4f}")

print("\n Рейтинг по Calinski-Harabasz Index (↑ выше = лучше):")
ch_ranking = sorted(zip(algs, ch_values), key=lambda x: x[1] if not np.isnan(x[1]) else -1, reverse=True)
for i, (alg, score) in enumerate(ch_ranking, 1):
    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
    if not np.isnan(score):
        print(f"   {medal} {i}. {alg:<15} {score:.0f}")

print("\nИнтерпретация результатов:")

best_sil_alg = sil_ranking[0][0]
best_sil_score = sil_ranking[0][1]

print(f"Лучший алгоритм по Silhouette Score: {best_sil_alg} ({best_sil_score:.4f})")
if best_sil_score > 0.7:
    print(f"      → Отличное качество кластеризации, кластеры чётко разделены")
elif best_sil_score > 0.5:
    print(f"      → Хорошее качество кластеризации, кластеры разделены")
elif best_sil_score > 0.25:
    print(f"      → Приемлемое качество, есть некоторое перекрытие кластеров")
else:
    print(f"      → Низкое качество, кластеры плохо разделены")

best_db_alg = db_ranking[0][0]
best_db_score = db_ranking[0][1]

print(f"Лучший алгоритм по Davies-Bouldin Index: {best_db_alg} ({best_db_score:.4f})")
if best_db_score < 1.0:
    print(f"      → Хорошее разделение кластеров")
else:
    print(f"      → Удовлетворительное разделение")

best_ch_alg = ch_ranking[0][0]
best_ch_score = ch_ranking[0][1]

print(f"Лучший алгоритм по Calinski-Harabasz Index: {best_ch_alg} ({best_ch_score:.0f})")
print(f"      → Кластеры компактные и хорошо разделённые")

print(f"\nСравнение с истинными метками:")
print(f"      - K-Means:       ARI = {kmeans_ari:.4f}, NMI = {kmeans_nmi:.4f}")
print(f"      - Agglomerative: ARI = {agg_ari:.4f}, NMI = {agg_nmi:.4f}")
print(f"      - DBSCAN:        ARI = {db_ari:.4f}, NMI = {db_nmi:.4f}")

if max(kmeans_ari, agg_ari, db_ari) < 0.3:
    print(f"\nНизкие значения ARI/NMI указывают на то, что найденные кластеры не совпадают с истинными архитектурами GPU.")
    print(f"Это нормально для unsupervised learning — алгоритмы группируют данные по числовым характеристикам, а не по предзаданным классам.")

print(f"\nИтоговая рекомендация:")
print(f"      Для данного датасета GPU лучше всего подходит алгоритм {best_sil_alg} с точки зрения внутренних метрик качества кластеризации.")
print("\nАнализ структуры данных и итоговое сравнение:")
print("Лучший алгоритм по Silhouette Score:")
best_idx = np.nanargmax([kmeans_sil, agg_sil, db_sil])
algs = ["K-Means", "Agglomerative", "DBSCAN"]
metrics = [kmeans_sil, agg_sil, db_sil]
print(f"   {algs[best_idx]} (Silhouette = {metrics[best_idx]:.4f})")

print("Структура данных влияет на результаты следующим образом:")
print("1) Если данные разделяются на компактные сферические кластеры, то K-Means/Agglomerative (ward) работают лучше.")
print("2) Если данные содержат выбросы, кластеры разного размера/формы или неявные границы — DBSCAN выявляет такую структуру надёжнее, но требует аккуратного подбора параметров.")
print("3) Визуализации (PCA и t-SNE) показывают, насколько кластеры реально отделимы.")
print("Для данного датасета GPU, оба метода (K-Means/ward) согласуются, но DBSCAN чувствителен к eps, допускает много выбросов и зачастую находит меньшее число крупных кластеров или много шума.")
print("Итог: Метод определяется характером данных и задачей анализа. При сильно пересекающихся группах, составных кластерах, шуме — лучше пробовать DBSCAN или t-SNE для качественной визуальной проверки структуры.")

"""5. Анализ результатов кластеризации"""
"""5.1. Визуализация 2D-проекций с окраской по кластерам"""

print("\n5.1. Визуализация 2D-проекций с окраской по кластерам:")

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_tsne = tsne.fit_transform(X_scaled)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
# KMeans
axes[0,0].scatter(X_pca[:,0], X_pca[:,1], c=kmeans_labels, cmap="tab10", s=18)
axes[0,0].set_title(f"PCA: K-Means (k={optimal_k})")
axes[1,0].scatter(X_tsne[:,0], X_tsne[:,1], c=kmeans_labels, cmap="tab10", s=18)
axes[1,0].set_title("t-SNE: K-Means")
# Agglomerative
axes[0,1].scatter(X_pca[:,0], X_pca[:,1], c=agg_labels, cmap="tab10", s=18)
axes[0,1].set_title(f"PCA: Agglomerative (k={n_clusters_agg})")
axes[1,1].scatter(X_tsne[:,0], X_tsne[:,1], c=agg_labels, cmap="tab10", s=18)
axes[1,1].set_title("t-SNE: Agglomerative")
# DBSCAN
axes[0,2].scatter(X_pca[:,0], X_pca[:,1], c=dbscan_labels, cmap="tab10", s=18)
axes[0,2].set_title(f"PCA: DBSCAN (noise=-1)")
axes[1,2].scatter(X_tsne[:,0], X_tsne[:,1], c=dbscan_labels, cmap="tab10", s=18)
axes[1,2].set_title("t-SNE: DBSCAN")
for ax in axes.flat:
    ax.set_xticks([])
    ax.set_yticks([])
plt.tight_layout()
plt.savefig("pca_tsne_cluster_projection.png", dpi=300, bbox_inches="tight")
plt.close()
print(" Сохранены графики: pca_tsne_cluster_projection.png")

print("\n5.2. Гистограммы размеров кластеров")
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# K-Means
u_k, c_k = np.unique(kmeans_labels, return_counts=True)
axes[0].bar(u_k, c_k, color="skyblue")
axes[0].set_title("K-Means")
axes[0].set_xlabel("Кластер")
axes[0].set_ylabel("Кол-во объектов")
axes[0].grid(axis='y', alpha=0.3)

# Agglomerative
u_a, c_a = np.unique(agg_labels, return_counts=True)
axes[1].bar(u_a, c_a, color="salmon")
axes[1].set_title("Agglomerative")
axes[1].set_xlabel("Кластер")
axes[1].set_ylabel("Кол-во объектов")
axes[1].grid(axis='y', alpha=0.3)

# DBSCAN
u_d, c_d = np.unique(dbscan_labels, return_counts=True)
axes[2].bar(u_d, c_d, color="lightgreen")
axes[2].set_title("DBSCAN (в т.ч. -1)")
axes[2].set_xlabel("Кластер")
axes[2].set_ylabel("Кол-во объектов")
axes[2].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig("cluster_sizes.png", dpi=300, bbox_inches="tight")
plt.close()
print("Сохранён график: cluster_sizes.png")

"""5.3. Boxplot-ы распределения признаков по кластерам"""

print("\n5.3. Boxplot-ы распределения признаков по кластерам:")
all_results = {
    'K-Means': kmeans_labels,
    'Agglomerative': agg_labels,
    'DBSCAN': dbscan_labels
}
for alg_name, labels in all_results.items():
    print(f"Boxplot для {alg_name}")
    df_plot = pd.DataFrame(X, columns=features)
    df_plot['cluster'] = labels
    # Не строим boxplot для выбросов DBSCAN: только для не-выбросов
    if alg_name == 'DBSCAN':
        df_plot = df_plot[df_plot['cluster'] != -1]
    plt.figure(figsize=(2*len(features), 5))
    sns.boxplot(data=df_plot, x='cluster', y=df_plot.columns[0])
    plt.title(f"Boxplot {df_plot.columns[0]} по кластерам {alg_name}")
    plt.savefig(f"boxplot_{alg_name}_feature1.png", dpi=200, bbox_inches="tight")
    plt.close()
    # Можно строить boxplot по всем признакам и кластеру (отдельным графиком)
    plt.figure(figsize=(2*len(features), 5))
    df_melt = df_plot.melt(id_vars=['cluster'], value_vars=features)
    sns.boxplot(data=df_melt, x='variable', y='value', hue='cluster', showfliers=False)
    plt.title(f"Boxplot всех признаков по кластерам {alg_name}")
    plt.savefig(f"boxplot_{alg_name}_all_features.png", dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Сохранены графики boxplot_{alg_name}_feature1.png, boxplot_{alg_name}_all_features.png")

# Вывод
print("Итоги")

print(f"""
Анализ завершён!
Результаты по качеству:
  K-Means:       Silhouette = {kmeans_sil:.4f}, ARI = {kmeans_ari:.4f}
  Agglomerative: Silhouette = {agg_sil:.4f}, ARI = {agg_ari:.4f}
  DBSCAN:        Silhouette = {db_sil:.4f}, выбросов = {outlier_pct:.1f}%
Лучший алгоритм по Silhouette Score: """, end="")

metrics = [kmeans_sil, agg_sil, db_sil]
algs = ["K-Means", "Agglomerative", "DBSCAN"]
best_idx = np.nanargmax(metrics)
print(f"{algs[best_idx]} ({metrics[best_idx]:.4f})")

"""6. Дополнительные задания"""
print("\n6. Дополнительные задания")
# 1. PCA для отбора признаков и сравнения кластеризации до/после
from sklearn.decomposition import PCA
print("Сравним кластеризацию ДО и ПОСЛЕ PCA (2 компоненты):")
# Кластеризация ДО
kmeans_before = KMeans(n_clusters=optimal_k, random_state=42, n_init=10).fit(X_scaled)
labels_before = kmeans_before.labels_
sil_before = silhouette_score(X_scaled, labels_before)
print(f"Silhouette до PCA: {sil_before:.4f}")
# PCA и кластеризация ПОСЛЕ
pca = PCA(n_components=2)
X_pca2 = pca.fit_transform(X_scaled)
kmeans_after = KMeans(n_clusters=optimal_k, random_state=42, n_init=10).fit(X_pca2)
labels_after = kmeans_after.labels_
sil_after = silhouette_score(X_pca2, labels_after)
print(f"Silhouette после PCA: {sil_after:.4f}")

# 2. GridSearchCV
from sklearn.metrics import silhouette_score
from sklearn.model_selection import GridSearchCV
from sklearn.cluster import KMeans

def silhouette_scorer(estimator, X):
    labels = estimator.fit_predict(X)
    n_clusters = len(set(labels))
    if n_clusters < 2:
        return -1
    return silhouette_score(X, labels)

grid = GridSearchCV(
    estimator=KMeans(random_state=42),
    param_grid={'n_clusters': range(2, 11)},
    scoring=silhouette_scorer,
    refit=True,
    n_jobs=-1
)
grid.fit(X_scaled)
print(f"Лучшее k для KMeans по silhouette: {grid.best_params_['n_clusters']} (score={grid.best_score_:.4f})")

# 3. KPrototypes(kmodes)
from kmodes.kprototypes import KPrototypes

# Пример: если есть категориальные признаки
if len(categorical_features) > 0:
    X_mixed = df_work[features + categorical_features].copy().values
    cat_idx = [X_mixed.shape[1]-len(categorical_features) + i for i in range(len(categorical_features))]
    # KPrototypes
    kproto = KPrototypes(n_clusters=optimal_k, random_state=42)
    labels_kproto = kproto.fit_predict(X_mixed, categorical=cat_idx)
    print(f"KPrototypes кластеризация: уникальных кластеров: {np.unique(labels_kproto)}")
    # Сравните с результатами KMeans на one-hot закодированных данных!
else:
    print("Категориальных признаков нет, KPrototypes не применяется.")

# 4. Сравнение с классификацией
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

rfc = RandomForestClassifier(random_state=42)
acc = cross_val_score(rfc, X_scaled, true_labels_encoded, cv=5, scoring='accuracy').mean()
print(f"Точность классификации (RandomForest): {acc:.4f}")
print(f"ARI для лучших кластеров: {max([kmeans_ari, agg_ari, db_ari]):.4f}")
print(f"NMI для лучших кластеров: {max([kmeans_nmi, agg_nmi, db_nmi]):.4f}")
