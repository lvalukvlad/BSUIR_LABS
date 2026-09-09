from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/help", tags=["Справка"])

class HelpSection(BaseModel):
    title: str
    content: str

class HelpResponse(BaseModel):
    sections: List[HelpSection]

@router.get("", response_model=HelpResponse)
def get_help():
    return HelpResponse(sections=[
        HelpSection(title="Загрузка", content="Поддерживаются TXT и RTF"),
        HelpSection(title="Анализ", content="Лемматизация и извлечение правил словоизменения"),
        HelpSection(title="Словарь", content="Поиск, фильтрация, редактирование записей"),
        HelpSection(title="Генерация", content="Укажите падеж/число/род для получения формы"),
        HelpSection(title="Сохранение", content="Словарь сохраняется в data/dictionary.json"),
    ])