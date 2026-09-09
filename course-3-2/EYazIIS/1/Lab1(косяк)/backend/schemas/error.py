from pydantic import BaseModel
from typing import Optional, Any


class ErrorResponse(BaseModel):
    """Стандартный формат ошибки API"""
    detail: str
    code: int = 400
    field: Optional[str] = None
    context: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Лемма не найдена",
                "code": 404,
                "field": "lemma",
                "context": {"value": "несуществующее_слово"}
            }
        }


class ValidationErrorResponse(BaseModel):
    """Ошибка валидации"""
    detail: str
    errors: list[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Ошибка валидации данных",
                "errors": [
                    {"field": "lemma", "message": "Поле обязательно"},
                    {"field": "pos", "message": "Неверное значение"}
                ]
            }
        }