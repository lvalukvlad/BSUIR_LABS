import re
from functools import lru_cache

import pymorphy3
import snowballstemmer

morph = pymorphy3.MorphAnalyzer()
de_stem = snowballstemmer.stemmer("german")

RU_RE = re.compile(r"[а-яё]+(?:-[а-яё]+)*", re.IGNORECASE)
DE_RE = re.compile(r"[a-zäöüß]+(?:-[a-zäöüß]+)*", re.IGNORECASE)

RU_STOP = {
    "а", "без", "более", "бы", "был", "была", "были", "было", "быть", "в", "вам",
    "вас", "во", "вот", "все", "всё", "всего", "всех", "вы", "где", "да", "даже",
    "для", "до", "его", "ее", "её", "если", "есть", "еще", "ещё", "же", "за", "и",
    "из", "или", "им", "их", "к", "как", "ко", "когда", "кто", "ли", "либо", "между",
    "мне", "может", "можно", "мы", "на", "над", "надо", "не", "него", "нее", "ней",
    "нет", "ни", "но", "о", "об", "он", "она", "они", "оно", "от", "по", "под",
    "после", "при", "про", "с", "со", "так", "также", "такой", "там", "то", "того",
    "тоже", "только", "том", "тот", "у", "уже", "чем", "через", "что", "чтобы",
    "эта", "эти", "это", "этого", "этой", "этом", "этот", "я",
}

DE_STOP = {
    "aber", "als", "am", "an", "auch", "auf", "aus", "bei", "bin", "bis", "das",
    "dass", "dem", "den", "der", "des", "die", "dies", "diese", "dieser", "dieses",
    "ein", "eine", "einem", "einen", "einer", "es", "für", "fur", "hat", "im", "in",
    "ist", "kein", "mit", "nach", "nicht", "oder", "sich", "sie", "sind", "und",
    "von", "vor", "war", "wie", "wird", "zu", "zum", "zur",
}


@lru_cache(maxsize=50_000)
def lemma(word, lang):
    w = word.lower().replace("ё", "е")
    if lang == "русский":
        parsed = morph.parse(w)
        if parsed:
            return parsed[0].normal_form.replace("ё", "е")
        return w
    return de_stem.stemWord(w)


def ok_word(w, lang):
    if len(w) < 3:
        return False
    stops = RU_STOP if lang == "русский" else DE_STOP
    return w not in stops


def tokenize(text, lang):
    pat = RU_RE if lang == "русский" else DE_RE
    out = []
    for m in pat.finditer(text):
        w = lemma(m.group(0), lang)
        if ok_word(w, lang):
            out.append(w)
    return out


def detect_language(text):
    letters = re.findall(r"[A-Za-zА-Яа-яЁёÄÖÜäöüß]", text)
    if not letters:
        return "немецкий"
    cyr = 0
    for ch in letters:
        low = ch.lower()
        if "а" <= low <= "я" or low == "ё":
            cyr += 1
    return "русский" if cyr / len(letters) >= 0.2 else "немецкий"
