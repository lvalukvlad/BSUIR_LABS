import re
from dataclasses import dataclass
from functools import lru_cache

import pymorphy3

_morph_ru = pymorphy3.MorphAnalyzer(lang="ru")

TOKEN_RE = re.compile(r"[а-яёa-zäöüß0-9]+(?:-[а-яёa-zäöüß0-9]+)*", re.IGNORECASE)

CYRILLIC_RE = re.compile(r"[а-яё]", re.IGNORECASE)
LATIN_RE = re.compile(r"[a-zäöüß]", re.IGNORECASE)

ABBREVIATIONS = {
    "ии", "лвс", "эвм", "субд", "бд", "днк", "сми", "гост",
    "usw", "zb", "bsp", "dh", "zb", "bzw", "etc",
}


@dataclass(frozen=True)
class Token:
    surface: str
    lemma: str
    start: int
    end: int


def detect_language(text: str) -> str:
    if not text:
        return "русский"
    cyr = len(CYRILLIC_RE.findall(text))
    lat = len(LATIN_RE.findall(text))
    if lat > cyr:
        return "немецкий"
    return "русский"


@lru_cache(maxsize=100_000)
def lemmatize(word: str, lang: str = "ru") -> str:
    lowered = word.lower().replace("ё", "е")
    if lowered in ABBREVIATIONS:
        return lowered
    if lang == "de":
        return lowered
    if not re.fullmatch(r"[а-я-]+", lowered):
        return lowered
    parsed = _morph_ru.parse(lowered)
    return parsed[0].normal_form.replace("ё", "е") if parsed else lowered


def reset_preprocess_cache() -> None:
    lemmatize.cache_clear()


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(text):
        surface = match.group(0)
        lang = "ru" if CYRILLIC_RE.search(surface) else "de"
        tokens.append(
            Token(
                surface=surface,
                lemma=lemmatize(surface, lang),
                start=match.start(),
                end=match.end(),
            )
        )
    return tokens


def lexemes(text: str) -> list[str]:
    return [token.lemma for token in tokenize(text) if token.lemma]


def normalize(text: str) -> list[str]:
    return [lemma for lemma in lexemes(text) if len(lemma) >= 2]
