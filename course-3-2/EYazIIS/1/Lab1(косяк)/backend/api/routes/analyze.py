"""
Эндпоинт анализа текста: загрузка → токенизация → лемматизация → словарь
Задание 2: русский язык, TXT/RTF, лексемы + правила словоизменения
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import time
from pathlib import Path

from razdel import tokenize
from core.parser.txt_parser import TxtParser
from core.parser.rtf_parser import RtfParser
from core.morphology.analyzer import RussianMorphAnalyzer  # ← Отсюда берём _extract_grammemes
from core.dictionary.repository import DictionaryRepository
from core.dictionary.models import LemmaEntry, MorphRule

router = APIRouter(tags=["Анализ"])

txt_parser = TxtParser()
rtf_parser = RtfParser()
morph = RussianMorphAnalyzer()
repo = DictionaryRepository()


# ✅ ИМПОРТИРУЕМ функцию конвертации из analyzer.py
from core.morphology.analyzer import _extract_grammemes


def _build_rules_for_lemma(lemma: str, morph_analyzer) -> list[dict]:
    """
    Построение правил с РУССКИМИ ключами (падеж, род, число).
    """
    rules = []
    try:
        parses = morph_analyzer.morph.parse(lemma)
        if not parses:
            return rules

        parse = parses[0]
        lexeme = getattr(parse, 'lexeme', [])

        for form in lexeme[:12]:
            if form.word.lower() == lemma.lower():
                continue

            # Вычисляем окончание
            word = form.word.lower()
            lemma_lower = lemma.lower()

            common = 0
            for a, b in zip(lemma_lower, word):
                if a == b:
                    common += 1
                else:
                    break
            ending = word[common:]

            # ✅ ИСПОЛЬЗУЕМ функцию конвертации в русские ключи!
            grammemes = _extract_grammemes(form.tag.grammemes)

            if grammemes.get('падеж') or grammemes.get('число'):
                rules.append({
                    "ending": ending,
                    "grammemes": grammemes  # {"падеж": "родительный", "род": "мужской", "число": "единственное"}
                })

        # Убираем дубликаты
        seen = set()
        unique = []
        for r in rules:
            key = (r['ending'], tuple(sorted(r['grammemes'].items())))
            if key not in seen:
                seen.add(key)
                unique.append(r)

        return unique[:15]

    except Exception as e:
        print(f"build_rules error: {e}")
        return []


@router.post("/analyze")
async def analyze_text(file: UploadFile = File(...)):
    """Анализ текста"""
    start_time = time.time()

    # 1. Парсинг файла
    filename = file.filename or "unknown"
    ext = filename.split(".")[-1].lower() if "." in filename else "txt"
    content = await file.read()

    if ext == "rtf":
        text = rtf_parser.parse(content)
    else:
        text = txt_parser.parse(content)

    # 2. Токенизация
    tokens = [t.text.lower() for t in tokenize(text) if t.text.isalpha()]

    # 3. Лемматизация
    lemmas_data: dict[str, LemmaEntry] = {}

    for token in tokens:
        try:
            parse = morph.morph.parse(token)[0]
            lemma = parse.normal_form
            pos_raw = parse.tag.POS or "UNKNOWN"

            pos_map = {
                "NOUN": "существительное", "ADJF": "прилагательное",
                "ADJS": "прилагательное", "VERB": "глагол", "INFN": "глагол",
                "ADV": "наречие", "PRON": "местоимение", "PRED": "предикатив",
                "NUM": "числительное", "INTJ": "междометие", "PREP": "предлог",
                "CONJ": "союз", "PART": "частица", "ADVB": "наречие"
            }
            pos = pos_map.get(pos_raw, pos_raw.lower())

            if lemma not in lemmas_data:
                rules_raw = _build_rules_for_lemma(lemma, morph)
                rules = [MorphRule.from_dict(r) if isinstance(r, dict) else r for r in rules_raw]

                lemmas_data[lemma] = LemmaEntry(
                    lemma=lemma,
                    stem=lemma,
                    pos=pos,
                    rules=rules,
                    frequency=1
                )
            else:
                lemmas_data[lemma].frequency += 1

        except Exception as e:
            print(f"Error processing token '{token}': {e}")
            continue

    # 4. Сохранение
    for entry in lemmas_data.values():
        repo.save(entry)

    # 5. Ответ
    return {
        "total_tokens": len(tokens),
        "unique_lemmas": len(lemmas_data),
        "lemmas": sorted(
            [e.to_dict() for e in lemmas_data.values()],
            key=lambda x: x["lemma"]
        ),
        "processing_time_ms": round((time.time() - start_time) * 1000),
        "file_info": {"name": filename, "format": ext}
    }