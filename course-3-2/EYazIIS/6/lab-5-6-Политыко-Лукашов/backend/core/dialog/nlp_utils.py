from functools import lru_cache

from nltk.tokenize import RegexpTokenizer

_tokenizer = RegexpTokenizer(r"[А-Яа-яЁёA-Za-z]+|\d+")


@lru_cache(maxsize=1)
def _morph():
    import pymorphy3

    return pymorphy3.MorphAnalyzer()


def tokenize(text: str) -> list[str]:
    return _tokenizer.tokenize(text.lower())


def lemmas(text: str) -> list[str]:
    morph = _morph()
    out = []
    for w in tokenize(text):
        p = morph.parse(w)
        if p:
            out.append(p[0].normal_form)
        else:
            out.append(w)
    return out


def lemmas_set(text: str) -> set[str]:
    return set(lemmas(text))


def corpus_normalize(text: str) -> str:
    return " ".join(lemmas(text))
