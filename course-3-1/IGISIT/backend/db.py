# backend/db.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Используем переменные окружения для Docker
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:password@localhost:5432/db2"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class IndicatorData(Base):
    """Модель данных для таблицы 'indicator_data'."""
    __tablename__ = "indicator_data"

    id = Column(Integer, primary_key=True, index=True) 
    year = Column(Integer, index=True, nullable=False)
    region = Column(String, index=True, nullable=False)
    indicator = Column(String, index=True, nullable=False)
    value = Column(Float, nullable=False)

def init_db():
    """Создает базу данных и все таблицы, если они не существуют."""
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ForecastResult(Base):
    """Модель для сохранения результатов прогноза."""
    __tablename__ = "forecast_result"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, index=True, nullable=False)
    region = Column(String, index=True, nullable=False)
    indicator = Column(String, index=True, nullable=False)
    value = Column(Float, nullable=False)
    model_name = Column(String, nullable=False) # Какая модель сделала прогноз

class TrainedModel(Base):
    """Модель для сохранения сериализованных обученных моделей."""
    __tablename__ = "trained_models"
    
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True, nullable=False)
    indicator = Column(String, index=True, nullable=False)
    model_data = Column(String) 

if __name__ == '__main__':
    print("Пересоздание таблиц в базе данных...")
    init_db()
    print("Таблицы успешно пересозданы.")