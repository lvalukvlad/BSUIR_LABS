from pydantic import BaseModel, Field
from typing import Optional, List


class MorphRuleRequest(BaseModel):
    ending: str
    grammemes: dict[str, str]


class LemmaCreateRequest(BaseModel):
    lemma: str = Field(..., min_length=1, description="Лемма")
    stem: Optional[str] = Field(None, description="Основа слова")
    pos: Optional[str] = Field(None, description="Часть речи")
    rules: Optional[List[MorphRuleRequest]] = Field(default_factory=list)
    frequency: Optional[int] = Field(0, description="Частота")
    meta: Optional[dict] = Field(None, description="Метаданные")
    morphology_info: str = Field("", description="Морфологическая информация (по ТЗ)")

    class Config:
        from_attributes = True