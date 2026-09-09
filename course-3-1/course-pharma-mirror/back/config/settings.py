import os
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения с валидацией"""

    # Ollama
    OLLAMA_BASE_URL: str = Field(
        default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11435"),
        description="URL сервера Ollama"
    )
    OLLAMA_MODEL: str = Field(
        default=os.getenv("OLLAMA_MODEL", "mistral:latest"),
        description="Модель Ollama для использования"
    )
    OLLAMA_TEMPERATURE: float = Field(
        default=float(os.getenv("OLLAMA_TEMPERATURE", "0.3")),
        ge=0.0, le=2.0,
        description="Температура для генерации (0.0-2.0)"
    )
    OLLAMA_TIMEOUT: int = Field(
        default=int(os.getenv("OLLAMA_TIMEOUT", "1300")),
        gt=0,
        description="Таймаут запросов к Ollama в секундах"
    )

    # Логирование
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Уровень логирования"
    )
    LOG_FILE: Optional[str] = Field(
        default=os.getenv("LOG_FILE"),
        description="Файл для записи логов (если None - только консоль)"
    )

    # Workflow
    MAX_CLARIFICATION_ATTEMPTS: int = Field(
        default=int(os.getenv("MAX_CLARIFICATION_ATTEMPTS", "3")),
        gt=0,
        description="Максимальное количество попыток уточнения"
    )
    MIN_SYMPTOMS_FOR_DIAGNOSIS: int = Field(
        default=int(os.getenv("MIN_SYMPTOMS_FOR_DIAGNOSIS", "1")),
        ge=0,
        description="Минимальное количество симптомов для диагностики"
    )
    CONFIDENCE_THRESHOLD: float = Field(
        default=float(os.getenv("CONFIDENCE_THRESHOLD", "0.6")),
        ge=0.0, le=1.0,
        description="Порог уверенности для диагноза"
    )

    # Безопасность
    ENABLE_CONTRANDICATIONS_CHECK: bool = Field(
        default=os.getenv("ENABLE_CONTRANDICATIONS_CHECK", "true").lower() == "true",
        description="Включить проверку противопоказаний"
    )
    ENABLE_SEVERITY_EVALUATION: bool = Field(
        default=os.getenv("ENABLE_SEVERITY_EVALUATION", "true").lower() == "true",
        description="Включить оценку серьезности"
    )

    # API
    API_HOST: str = Field(
        default=os.getenv("API_HOST", "0.0.0.0"),
        description="Хост для FastAPI"
    )
    API_PORT: int = Field(
        default=int(os.getenv("API_PORT", "8000")),
        gt=0, lt=65536,
        description="Порт для FastAPI"
    )
    API_WORKERS: int = Field(
        default=int(os.getenv("API_WORKERS", "1")),
        gt=0,
        description="Количество воркеров FastAPI"
    )

    # CORS - только для разработки!
    CORS_ALLOW_ORIGINS: List[str] = Field(
        default=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
        description="Разрешенные origins для CORS"
    )

    # Производительность
    MAX_CONCURRENT_AGENTS: int = Field(
        default=int(os.getenv("MAX_CONCURRENT_AGENTS", "5")),
        gt=0,
        description="Максимальное количество параллельных агентов"
    )
    AGENT_TIMEOUT_SECONDS: int = Field(
        default=int(os.getenv("AGENT_TIMEOUT_SECONDS", "1300")),
        gt=0,
        description="Таймаут выполнения агента в секундах"
    )

    # Пути
    DATA_DIR: str = Field(
        default=os.getenv("DATA_DIR", "data"),
        description="Директория для данных"
    )
    MODEL_CACHE_DIR: str = Field(
        default=os.getenv("MODEL_CACHE_DIR", ".cache"),
        description="Директория для кэша моделей"
    )

    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()

    @validator('OLLAMA_BASE_URL')
    def validate_ollama_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('OLLAMA_BASE_URL must start with http:// or https://')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


# Экземпляр настроек с ленивой инициализацией
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Возвращает экземпляр настроек (синглтон)"""
    global _settings_instance

    if _settings_instance is None:
        _settings_instance = Settings()

    return _settings_instance