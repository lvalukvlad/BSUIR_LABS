from fastapi import APIRouter
from pydantic import BaseModel

from core.dictionary.repository import DictionaryRepository
from core.morphology.analyzer import RussianMorphAnalyzer

router = APIRouter(tags=["Генерация"])
repo = DictionaryRepository()
morph = RussianMorphAnalyzer()

GRAMMEME_MAP = {
    'именительный': 'nomn', 'родительный': 'gent', 'дательный': 'datv',
    'винительный': 'accs', 'творительный': 'ablt', 'предложный': 'loct',
    'ед': 'sing', 'мн': 'plur', 'единственное': 'sing', 'множественное': 'plur',
    'муж': 'masc', 'жен': 'femn', 'ср': 'neut',
    'наст': 'pres', 'буд': 'futn', 'прош': 'past',
}


class GenerateRequest(BaseModel):
    lemma: str
    grammemes: dict[str, str]


def _normalize_tags(input_grammemes: dict) -> set:
    result = set()
    for k, v in input_grammemes.items():
        if k.lower() in ('case', 'number', 'gender', 'падеж', 'число', 'род'):
            normalized = GRAMMEME_MAP.get(v.lower(), v.lower())
            if normalized and normalized not in ('true', 'false', None, ''):
                result.add(normalized)
        else:
            normalized = GRAMMEME_MAP.get(v.lower(), v.lower())
            if normalized and normalized not in ('true', 'false', None, ''):
                result.add(normalized)
    return result


@router.post("/generate")
def generate_form(request: GenerateRequest):
    target_tags = _normalize_tags(request.grammemes)
    entry = repo.get(request.lemma)

    if entry and entry.rules:
        for rule in entry.rules:
            rule_values = {k.lower(): v.lower() if isinstance(v, str) else str(v).lower() 
                          for k, v in rule.grammemes.items()}
            
            match = True
            for k, v in request.grammemes.items():
                key_map = {
                    'падеж': 'падеж',
                    'число': 'число',
                    'род': 'род',
                }
                rule_key = key_map.get(k.lower(), k.lower())
                if rule_key in rule_values:
                    normalized_v = v.lower()
                    if rule_values[rule_key] != normalized_v:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                form = entry.stem + rule.ending
                return {
                    "form": form,
                    "source_rule": {"ending": rule.ending, "grammemes": rule.grammemes},
                    "from_dictionary": True
                }

    try:
        parses = morph.morph.parse(request.lemma)
        for p in parses:
            if target_tags.issubset({g.lower() for g in p.tag.grammemes}):
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
        "error": "Правило не найдено",
        "requested_tags": list(target_tags)
    }