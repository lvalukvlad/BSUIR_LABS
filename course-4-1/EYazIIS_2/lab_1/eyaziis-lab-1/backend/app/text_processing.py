import re
from dataclasses import dataclass
from functools import lru_cache

import pymorphy3

_morph = pymorphy3.MorphAnalyzer()

TOKEN_RE = re.compile(r"[а-яёa-z0-9]+(?:-[а-яёa-z0-9]+)*", re.IGNORECASE)

MIN_TOKEN_LEN = 2

ABBREVIATIONS = {"ии", "лвс", "эвм", "субд", "бд", "днк", "сми", "гост"}

STOPWORDS = {
    "а", "без", "более", "больше", "будет", "будто", "бы", "был", "была", "были",
    "было", "быть", "в", "вам", "вас", "ведь", "весь", "вдруг", "во", "вот",
    "впрочем", "все", "всё", "всего", "всех", "всю", "вы", "где", "да", "давать",
    "даже", "два", "для", "до", "другой", "его", "ее", "её", "ей", "ему", "если",
    "есть", "ещё", "еще", "же", "за", "здесь", "и", "из", "или", "им", "иметь",
    "их", "к", "как", "какой", "когда", "конечно", "которая", "которого",
    "которое", "которой", "котором", "которую", "которые", "который", "которых",
    "кто", "куда", "ли", "лучше", "между", "меня", "мне", "много", "может",
    "можно", "мой", "мы", "на", "над", "надо", "наконец", "нас", "не", "него",
    "неё", "нее", "ней", "нельзя", "нет", "ни", "нибудь", "никогда", "ним", "них",
    "ничего", "но", "ну", "о", "об", "однако", "он", "она", "они", "оно", "от",
    "очень", "перед", "по", "под", "после", "потом", "потому", "почти", "при",
    "про", "раз", "разве", "с", "сам", "свой", "себя", "сейчас", "снова", "со",
    "совсем", "так", "такой", "там", "те", "тем", "теперь", "то", "тоже",
    "только", "том", "тот", "три", "тут", "ты", "у", "уже", "хорошо", "хоть",
    "чего", "чей", "чем", "через", "что", "чтобы", "чуть", "эта", "эти", "этих",
    "это", "этого", "этой", "этом", "этот", "эту", "я",
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were",
}


@dataclass(frozen=True)
class Token:

    surface: str
    lemma: str
    start: int
    end: int


@lru_cache(maxsize=100_000)
def lemmatize(word: str) -> str:
    lowered = word.lower().replace("ё", "е")
    if lowered in ABBREVIATIONS:
        return lowered
    if not re.fullmatch(r"[а-я-]+", lowered):
        return lowered
    parsed = _morph.parse(lowered)
    return parsed[0].normal_form.replace("ё", "е") if parsed else lowered


def is_meaningful(lemma: str) -> bool:
    return len(lemma) >= MIN_TOKEN_LEN and lemma not in STOPWORDS


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(text):
        surface = match.group(0)
        tokens.append(
            Token(
                surface=surface,
                lemma=lemmatize(surface),
                start=match.start(),
                end=match.end(),
            )
        )
    return tokens


def normalize(text: str) -> list[str]:
    return [t.lemma for t in tokenize(text) if is_meaningful(t.lemma)]
