from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db import IndicatorData, ForecastResult, get_db, SessionLocal

# --- FastAPI APP ---
app = FastAPI(
    title="Belarus Economic Indicators API (v1.2)",
    description="API для доступа к временным рядам экономических данных Беларуси, включая прогнозы.",
    version="1.2.0"
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel


# ===========
#  SCHEMAS
# ===========
class IndicatorResponse(BaseModel):
    year: int
    region: str
    indicator: str
    value: float
    class Config:
        from_attributes = True


class ForecastResponse(BaseModel):
    year: int
    region: str
    indicator: str
    value: float
    model_name: str
    class Config:
        from_attributes = True


# --- ОБЪЕДИНЁННАЯ СХЕМА ---
class CombinedResponse(BaseModel):
    year: int
    region: str
    indicator: str
    value: float
    source: str                 # "historical" | "forecast"
    model_name: str | None = None

    class Config:
        from_attributes = True


# =============================
#  METADATA FUNCTIONS
# =============================
def get_unique_indicators(db: Session) -> List[str]:
    return [item[0] for item in db.query(IndicatorData.indicator).distinct().all()]

def get_unique_regions(db: Session) -> List[str]:
    return [item[0] for item in db.query(IndicatorData.region).distinct().all()]


# =============================
#  DATA FUNCTIONS
# =============================
def get_data_by_indicator(db: Session, indicator_name: str) -> List[IndicatorData]:
    return db.query(IndicatorData).filter(
        IndicatorData.indicator == indicator_name
    ).order_by(IndicatorData.year).all()

def get_data_by_region(db: Session, region_name: str) -> List[IndicatorData]:
    return db.query(IndicatorData).filter(
        IndicatorData.region == region_name
    ).order_by(IndicatorData.indicator, IndicatorData.year).all()

def get_forecast_by_indicator(db: Session, indicator_name: str) -> List[ForecastResult]:
    return db.query(ForecastResult).filter(
        ForecastResult.indicator == indicator_name
    ).order_by(ForecastResult.year).all()

def get_forecast_by_region(db: Session, region_name: str) -> List[ForecastResult]:
    return db.query(ForecastResult).filter(
        ForecastResult.region == region_name
    ).order_by(ForecastResult.indicator, ForecastResult.year).all()


# =============================
#  METADATA ENDPOINTS
# =============================
@app.get("/metadata/indicators", response_model=List[str], tags=["Metadata"])
def read_available_indicators(db: Session = Depends(get_db)):
    return get_unique_indicators(db)

@app.get("/metadata/regions", response_model=List[str], tags=["Metadata"])
def read_available_regions(db: Session = Depends(get_db)):
    return get_unique_regions(db)


# =============================
#   HISTORICAL DATA ENDPOINTS
# =============================
@app.get(
    "/data/indicator/{indicator_name}",
    response_model=List[IndicatorResponse],
    tags=["Historical Data"]
)
def read_by_indicator(indicator_name: str, db: Session = Depends(get_db)):
    data = get_data_by_indicator(db, indicator_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Историческая метрика '{indicator_name}' не найдена.")
    return data


# =============================================
#   ОБЪЕДИНЁННЫЙ ЭНДПОИНТ /data/region/{region}
# =============================================
@app.get(
    "/data/region/{region_name}",
    response_model=List[CombinedResponse],
    tags=["Historical Data"],
    summary="Исторические + прогнозные данные по региону (объединено)"
)
def read_by_region(region_name: str, db: Session = Depends(get_db)):
    historical = get_data_by_region(db, region_name)
    forecast = get_forecast_by_region(db, region_name)

    if not historical and not forecast:
        raise HTTPException(
            status_code=404,
            detail=f"Нет данных для региона '{region_name}'"
        )

    combined = []

    for item in historical:
        combined.append(
            CombinedResponse(
                year=item.year,
                region=item.region,
                indicator=item.indicator,
                value=item.value,
                source="historical"
            )
        )

    for item in forecast:
        combined.append(
            CombinedResponse(
                year=item.year,
                region=item.region,
                indicator=item.indicator,
                value=item.value,
                source="forecast",
                model_name=item.model_name
            )
        )

    combined.sort(key=lambda x: (x.indicator, x.year))
    return combined


# ==================================================
#   /forecast/region/{region_name} — теперь ТО ЖЕ
# ==================================================
@app.get(
    "/forecast/region/{region_name}",
    response_model=List[CombinedResponse],
    tags=["Forecast Data"],
    summary="Исторические + прогнозные данные по региону (объединено)"
)
def read_forecast_region(region_name: str, db: Session = Depends(get_db)):
    return read_by_region(region_name, db)


# ======================================
#   FORECAST BY INDICATOR — не менялся
# ======================================
@app.get(
    "/forecast/indicator/{indicator_name}",
    response_model=List[ForecastResponse],
    tags=["Forecast Data"]
)
def read_forecast_by_indicator(indicator_name: str, db: Session = Depends(get_db)):
    data = get_forecast_by_indicator(db, indicator_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Прогноз для метрики '{indicator_name}' не найден.")
    return data


# ======================================
#             APP STARTUP
# ======================================
if __name__ == '__main__':
    import uvicorn

    print("Запуск FastAPI сервера: http://127.0.0.1:8000")
    print("Документация: http://127.0.0.1:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)
