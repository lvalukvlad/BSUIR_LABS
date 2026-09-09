from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class MorphRuleResponse(BaseModel):
    ending: str
    grammemes: dict[str, str]


class LemmaResponse(BaseModel):
    lemma: str = Field(..., description="Лемма (начальная форма)")
    stem: str = Field(..., description="Основа слова")
    pos: str = Field(..., description="Часть речи")
    rules: List[MorphRuleResponse] = Field(default_factory=list)
    frequency: int = Field(0, description="Частота встречаемости")
    meta: Optional[dict] = Field(None, description="Доп. метаданные")
    morphology_info: str = Field("", description="Морфологическая информация")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str
    code: int = 400

__all__ = ['MorphRuleResponse', 'LemmaResponse', 'ErrorResponse']