from fastapi import APIRouter, UploadFile, File, HTTPException
import time
from pathlib import Path
from razdel import tokenize
from core.parser.txt_parser import TxtParser
from core.parser.rtf_parser import RtfParser
from core.morphology.analyzer import RussianMorphAnalyzer
from core.dictionary.repository import DictionaryRepository
from core.dictionary.models import LemmaEntry, MorphRule

router = APIRouter(tags=["Анализ"])
txt_parser = TxtParser()
rtf_parser = RtfParser()
morph = RussianMorphAnalyzer()
repo = DictionaryRepository()

from core.morphology.analyzer import _extract_grammemes


def _extract_stem(lemma: str, morph_analyzer) -> str:
    lemma_lower = lemma.lower()
    try:
        parses = morph_analyzer.morph.parse(lemma_lower)
        if parses:
            parse = parses[0]
            lexeme = getattr(parse, 'lexeme', [])

            for form in lexeme[:10]:
                word = form.word.lower()
                if word != lemma_lower and len(word) > len(lemma_lower):
                    common = 0
                    for a, b in zip(lemma_lower, word):
                        if a == b:
                            common += 1
                        else:
                            break
                    if common > 0:
                        stem = lemma_lower[:common]
                        if len(stem) > 0:
                            return stem
    except Exception as e:
        print(f"Error extracting stem for '{lemma}': {e}")

    vowels = 'аеёиоуыэюя'
    for i in range(len(lemma_lower) - 1, -1, -1):
        if lemma_lower[i] in vowels:
            return lemma_lower[:i+1] if i > 0 else lemma_lower
    
    return lemma_lower


def _build_rules_for_lemma(lemma: str, morph_analyzer) -> list[dict]:
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

            word = form.word.lower()
            lemma_lower = lemma.lower()

            common = 0
            for a, b in zip(lemma_lower, word):
                if a == b:
                    common += 1
                else:
                    break
            ending = word[common:]

            grammemes = _extract_grammemes(form.tag.grammemes)

            if grammemes.get('падеж') or grammemes.get('число'):
                rules.append({
                    "ending": ending,
                    "grammemes": grammemes
                })

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
    start_time = time.time()

    filename = file.filename or "unknown"
    ext = filename.split(".")[-1].lower() if "." in filename else "txt"
    content = await file.read()

    if ext == "rtf":
        text = rtf_parser.parse(content)
    else:
        text = txt_parser.parse(content)

    tokens = [t.text.lower() for t in tokenize(text) if t.text.isalpha()]

    lemmas_data: dict[str, LemmaEntry] = {}

    for token in tokens:
        try:
            parse = morph.morph.parse(token)[0]
            lemma = parse.normal_form.strip().lower()
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
                stem = _extract_stem(lemma, morph)

                lemmas_data[lemma] = LemmaEntry(
                    lemma=lemma,
                    stem=stem,
                    pos=pos,
                    rules=rules,
                    frequency=1
                )
            else:
                lemmas_data[lemma].frequency += 1

        except Exception as e:
            print(f"Error processing token '{token}': {e}")
            continue

    for entry in lemmas_data.values():
        repo.save(entry)

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