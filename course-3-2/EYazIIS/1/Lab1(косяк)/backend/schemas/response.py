"""
Схемы ответов API (Pydantic v2)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class MorphRuleResponse(BaseModel):
    """Правило словоизменения"""
    ending: str
    grammemes: dict[str, str]


class LemmaResponse(BaseModel):
    lemma: str = Field(..., description="Лемма (начальная форма)")
    stem: str = Field(..., description="Основа слова")
    pos: str = Field(..., description="Часть речи")
    rules: List[MorphRuleResponse] = Field(default_factory=list)
    frequency: int = Field(0, description="Частота встречаемости")
    meta: Optional[dict] = Field(None, description="Доп. метаданные")

    class Config:
        from_attributes = True  # Для совместимости с dataclass


class ErrorResponse(BaseModel):
    """Стандартный ответ об ошибке"""
    detail: str
    code: int = 400


# Явный экспорт для импортов
__all__ = ['MorphRuleResponse', 'LemmaResponse', 'ErrorResponse']