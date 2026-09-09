# train_predict_save.py

import pandas as pd
import os
from sqlalchemy.orm import Session
from joblib import dump
from prophet import Prophet
import matplotlib.pyplot as plt

# Убедитесь, что database.py находится в той же папке
from db import IndicatorData, ForecastResult, TrainedModel, SessionLocal, init_db, engine 

# --- КОНФИГУРАЦИЯ ---
MODEL_SAVE_DIR = "saved_models" 
PLOTS_SAVE_DIR = "forecast_plots" 
# Горизонт прогноза (на сколько лет вперед прогнозируем)
FORECAST_PERIOD = 3 
# Горизонт прогноза назад (на сколько лет назад прогнозируем недостающие данные)
BACKWARD_FORECAST_PERIOD = 2 

# --- НОВАЯ КОНФИГУРАЦИЯ МОДЕЛИ ---
# Меньшее значение (например, 0.005) делает тренд менее гибким и более сглаженным.
# Стандартное значение: 0.05
CHANGEPOINT_PRIOR_SCALE = 0.005 

# --- КОНФИГУРАЦИЯ ОБРАБОТКИ ВЫБРОСОВ ---
# Коэффициент для IQR. 1.5 - стандартный (Box Plot). Можно увеличить до 3.0 для менее строгой фильтрации.
IQR_FACTOR = 3.0 

# =====================================================
# НОВАЯ КОНФИГУРАЦИЯ ОГРАНИЧЕНИЙ ДЛЯ ПРОБЛЕМНЫХ МЕТРИК
# =====================================================

CAP_FLOOR_CONFIG = {
    # 'Unemployed_Count': Численность не может быть отрицательной, и должна замедлить падение.
    'Число безработных': {'cap_factor': 1.2, 'floor_abs': 200.0, 'growth': 'logistic'},
    
    # 'Inflation_CPI': Инфляция также не может быть отрицательной (или очень близка к 0).
    'Инфляция ИПЦ': {'cap_factor': 1.5, 'floor_abs': 5.0, 'growth': 'logistic'},
}


def handle_outliers(df: pd.DataFrame, column: str, iqr_factor: float) -> pd.DataFrame:
    """
    Идентифицирует выбросы с помощью метода IQR и заменяет их на NaN.
    Prophet будет интерполировать эти точки.
    """
    # Вычисляем квартили и IQR
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    # Определяем границы для выбросов
    lower_bound = Q1 - iqr_factor * IQR
    upper_bound = Q3 + iqr_factor * IQR
    
    # Маска для выбросов
    outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    
    # Замена выбросов на NaN (Prophet будет их интерполировать)
    df_clean = df.copy()
    num_outliers = outlier_mask.sum()

    if num_outliers > 0:
        print(f"    ⚠️ Обнаружено и обработано {num_outliers} выбросов (IQR Factor: {iqr_factor}).")
        df_clean.loc[outlier_mask, column] = pd.NaT # Prophet требует NaT для 'y'
        
    return df_clean

# =====================================================
# ГЛАВНАЯ ФУНКЦИЯ: Обучение и Прогноз
# =====================================================

def train_and_forecast():
    """Главная функция для обучения, прогнозирования, сохранения моделей и графиков."""
    
    # Инициализация и создание папок
    init_db()
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    os.makedirs(PLOTS_SAVE_DIR, exist_ok=True) 
    db: Session = SessionLocal()
    
    try:
        # 1. Загрузка данных из БД
        print("1. Загрузка исходных данных из БД...")
        query = db.query(IndicatorData)
        df_all = pd.read_sql(query.statement, engine)
        
        if df_all.empty:
            print("ОШИБКА: Исходные данные в таблице 'indicator_data' не найдены.")
            return

        unique_regions = df_all['region'].unique()
        unique_indicators = df_all['indicator'].unique()
        
        print(f"Найдено {len(unique_regions)} регионов и {len(unique_indicators)} индикаторов для прогноза.")
        
        all_forecasts = []

        # 2. Обучение и прогнозирование для каждого РЕГИОНА и каждого ИНДИКАТОРА
        for region in unique_regions:
            print(f"\n===== Обработка региона: {region} =====")
            df_region = df_all[df_all['region'] == region]

            for indicator in unique_indicators:
                print(f"--- Индикатор: {indicator} ---")
                
                # 2.1 Подготовка данных для Prophet
                df_ts = df_region[df_region['indicator'] == indicator].copy()
                
                # Создаем дату
                df_ts['ds'] = pd.to_datetime(df_ts['year'], format='%Y')
                df_ts.rename(columns={'value': 'y'}, inplace=True)
                
                # Убедимся, что данных достаточно (минимум 5 точек для адекватности)
                if len(df_ts) < 5:
                     print(f"Пропуск: недостаточно данных ({len(df_ts)} записей для {region}).")
                     continue
                
                # Обработка выбросов
                df_ts = handle_outliers(df_ts, 'y', IQR_FACTOR)
                
                # ⚙️ ПРИМЕНЕНИЕ ЛОГИСТИЧЕСКОГО РОСТА И ОГРАНИЧЕНИЙ (CAP/FLOOR)
                model_growth = 'linear' # По умолчанию
                
                if indicator in CAP_FLOOR_CONFIG:
                    config = CAP_FLOOR_CONFIG[indicator]
                    model_growth = config['growth']
                    print(f"    🌟 Активирован **логистический рост** с ограничениями.")

                    # Установка CAP (верхний предел): Макс. историческое значение * фактор
                    max_val = df_ts['y'].max()
                    cap_val = max_val * config['cap_factor']
                    df_ts['cap'] = cap_val
                    
                    # Установка FLOOR (нижний предел): Абсолютное значение
                    floor_val = config['floor_abs']
                    df_ts['floor'] = floor_val
                    
                    # Prophet требует, чтобы floor < y < cap
                    # Гарантируем, что floor ниже всех исторических y
                    df_ts['floor'] = df_ts['floor'].apply(lambda x: min(x, df_ts['y'].min() * 0.9))
                    
                    # Проверка на ошибки: cap должен быть больше максимального значения y
                    if df_ts['cap'].min() <= df_ts['y'].max():
                        print(f"    ❌ ОШИБКА: Cap ({df_ts['cap'].min():.2f}) меньше или равен максимальному Y ({df_ts['y'].max():.2f}). Увеличьте cap_factor.")
                        # Временно переключаемся на linear, чтобы не сломать модель
                        model_growth = 'linear'
                        df_ts.drop(columns=['cap', 'floor'], inplace=True)


                # 2.2 Настройка и обучение модели ⚙️
                model = Prophet(
                    yearly_seasonality=False,
                    weekly_seasonality=False,
                    daily_seasonality=False,
                    changepoint_prior_scale=CHANGEPOINT_PRIOR_SCALE, # Снижаем для консервативного прогноза
                    growth=model_growth # Используем 'linear' или 'logistic'
                )
                
                model.fit(df_ts)
                
                # 2.3 Прогнозирование (включая прогноз назад для интерполяции/экстраполяции)
                
                # Определяем количество периодов для прогноза (вперед) и истории (назад)
                periods_forward = FORECAST_PERIOD
                
                # Рассчитываем количество периодов назад для заполнения недостающих данных
                # Прогноз назад имеет смысл, если данных меньше, чем мы хотим заполнить
                min_year = df_ts['year'].min()
                if min_year > 1990: # Предполагаем, что данные начинаются с 1990 или раньше
                    periods_backward = min(BACKWARD_FORECAST_PERIOD, min_year - 1990)
                else:
                    periods_backward = 0
                
                # Создаем DataFrame для прогноза
                future = model.make_future_dataframe(
                    periods=periods_forward, 
                    freq='YE', 
                    include_history=True
                )
                
                # Если нужна экстраполяция назад, добавляем недостающие годы
                if periods_backward > 0:
                    start_date = pd.to_datetime(f'{min_year - periods_backward}-12-31')
                    
                    # Создаем недостающие года до начала имеющихся данных
                    df_backward = pd.DataFrame({
                        'ds': pd.date_range(start=start_date, end=df_ts['ds'].min(), freq='YE')
                    })
                    
                    # Объединяем, чтобы получить полный диапазон ds
                    future = pd.concat([df_backward, future]).drop_duplicates(subset=['ds']).sort_values('ds').reset_index(drop=True)
                
                
                # Применяем cap/floor, если используется логистический рост
                if model_growth == 'logistic':
                    # Применяем cap/floor ко всему диапазону ds (история + прогноз)
                    future['cap'] = df_ts['cap'].iloc[0]
                    future['floor'] = df_ts['floor'].iloc[0]
                    
                forecast = model.predict(future)
                
                # 2.4 Генерация и сохранение графика 🖼️
                safe_name = f"{region.replace(' ', '_').replace('.', '')}_{indicator.replace(' ', '_')}"
                plot_filepath = os.path.join(PLOTS_SAVE_DIR, f'прогноз_{safe_name}.png')

                fig = model.plot(forecast)
                ax = fig.gca()
                ax.set_title(f"Прогноз: {indicator} ({region}) (Growth: {model_growth})", fontsize=14)
                ax.set_xlabel("Год", fontsize=12)
                ax.set_ylabel("Значение", fontsize=12)
                
                fig_comp = model.plot_components(forecast)
                fig_comp.tight_layout() 
                
                # Сохраняем главный график
                plt.figure(fig)
                plt.savefig(plot_filepath, bbox_inches='tight')
                plt.close(fig)
                
                # Сохраняем график компонентов (для отладки)
                plot_comp_filepath = os.path.join(PLOTS_SAVE_DIR, f'компоненты_{safe_name}.png')
                plt.figure(fig_comp)
                plt.savefig(plot_comp_filepath, bbox_inches='tight')
                plt.close(fig_comp)
                
                print(f"    Графики прогноза и компонентов сохранены.")
                
                # 2.5 Сохранение обученной модели (joblib)
                model_filepath = os.path.join(MODEL_SAVE_DIR, f'{safe_name}_prophet_model.joblib')
                dump(model, model_filepath)
                
                # Сохранение пути к модели в БД
                model_entry = TrainedModel(
                    region=region,
                    indicator=indicator, 
                    model_data=model_filepath 
                )
                db.merge(model_entry)
                
                # 2.6 Подготовка результатов прогноза для сохранения в БД
                max_hist_year = df_ts['year'].max()
                
                # Фильтруем все прогнозные данные (вперед и назад), которые НЕ являются историческими точками
                historical_years = df_ts['year'].unique()
                df_forecast = forecast[['ds', 'yhat']].copy()
                df_forecast['year'] = df_forecast['ds'].dt.year
                
                # Оставляем только те годы, которых нет в исходных данных
                df_forecast = df_forecast[~df_forecast['year'].isin(historical_years)].copy()
                
                
                df_forecast['region'] = region 
                df_forecast['indicator'] = indicator
                df_forecast.rename(columns={'yhat': 'value'}, inplace=True)
                
                # 🎯 Округление до сотых
                if indicator=='Доля в мировом ВВП':
                     df_forecast['value'] = df_forecast['value'].round(4)
                else:
                    df_forecast['value'] = df_forecast['value'].round(0)
                
                df_forecast['model_name'] = 'Prophet_Logistic' if model_growth == 'logistic' else 'Prophet_Linear'
                
                all_forecasts.append(df_forecast[['year', 'region', 'indicator', 'value', 'model_name']])

        # 3. Сохранение всех прогнозов в БД
        if all_forecasts:
            df_final_forecast = pd.concat(all_forecasts, ignore_index=True)
            
            db.query(ForecastResult).delete()
            db.commit()
            print(f"\n3. Таблица '{ForecastResult.__tablename__}' очищена.")
            
            df_final_forecast.to_sql(ForecastResult.__tablename__, con=engine, if_exists='append', index=False)
            
            print(f"✅ Успешно сохранено {len(df_final_forecast)} прогнозных записей в БД.")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Произошла критическая ошибка: {e}")
    finally:
        db.close()
        
if __name__ == '__main__':
    train_and_forecast()