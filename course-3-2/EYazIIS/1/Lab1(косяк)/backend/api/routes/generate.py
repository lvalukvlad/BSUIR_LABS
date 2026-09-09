"""Эндпоинт генерации словоформ"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.dictionary.repository import DictionaryRepository
from core.morphology.analyzer import RussianMorphAnalyzer

router = APIRouter(tags=["Генерация"])
repo = DictionaryRepository()
morph = RussianMorphAnalyzer()

# Внутренний маппинг (НЕ виден в API!)
_CASE_MAP_REVERSE = {
    'именительный': 'nomn',
    'родительный': 'gent',
    'дательный': 'datv',
    'винительный': 'accs',
    'творительный': 'ablt',
    'предложный': 'loct'
}

_NUMBER_MAP_REVERSE = {
    'единственное': 'sing',
    'множественное': 'plur'
}

_GENDER_MAP_REVERSE = {
    'мужской': 'masc',
    'женский': 'femn',
    'средний': 'neut'
}


def _to_pymorphy2_tags(grammemes: dict) -> set:
    """Конвертирует русские граммемы в теги pymorphy2 (внутренняя функция)"""
    tags = set()

    if grammemes.get('падеж'):
        tag = _CASE_MAP_REVERSE.get(grammemes['падеж'])
        if tag:
            tags.add(tag)

    if grammemes.get('число'):
        tag = _NUMBER_MAP_REVERSE.get(grammemes['число'])
        if tag:
            tags.add(tag)

    if grammemes.get('род'):
        tag = _GENDER_MAP_REVERSE.get(grammemes['род'])
        if tag:
            tags.add(tag)

    return tags


class GenerateRequest(BaseModel):
    lemma: str
    grammemes: dict[str, str]


@router.post("/generate")
def generate_form(request: GenerateRequest):
    """Генерация словоформы"""

    target_tags = _to_pymorphy2_tags(request.grammemes)
    entry = repo.get(request.lemma)

    if entry and entry.rules:
        for rule in entry.rules:
            match = True
            for key in ['падеж', 'число', 'род']:
                if key in request.grammemes and request.grammemes[key]:
                    if rule.grammemes.get(key) != request.grammemes[key]:
                        match = False
                        break

            if match:
                form = entry.stem + rule.ending
                return {
                    "form": form,
                    "source_rule": {
                        "ending": rule.ending,
                        "grammemes": rule.grammemes
                    },
                    "from_dictionary": True
                }

    # Fallback через pymorphy2
    try:
        parses = morph.morph.parse(request.lemma)
        for p in parses:
            if target_tags.issubset(p.tag.grammemes):
                return {
                    "form": p.word,
                    "source_rule": None,
                    "from_fallback": True
                }
    except Exception:
        pass

    return {
        "form": request.lemma,
        "source_rule": None,
        "error": "Правило не найдено"
    }