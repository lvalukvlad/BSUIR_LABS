import html
import re

from .config import SNIPPET_WINDOW
from .db import fetch_all
from .text_processing import ABBREVIATIONS, is_meaningful, lemmatize, normalize, tokenize

MAX_EDIT_DISTANCE = 2
SUGGEST_LIMIT = 8

THESAURUS: dict[str, list[str]] = {
    "ии": ["искусственный", "интеллект"],
    "интеллект": ["ии"],
    "лвс": ["локальный", "сеть"],
    "эвм": ["компьютер"],
    "компьютер": ["эвм"],
    "нейросеть": ["нейронный", "сеть"],
    "автомобиль": ["машина"],
    "космос": ["космический"],
    "медицина": ["медицинский", "врач"],
    "спорт": ["спортивный"],
    "алгоритм": ["метод"],
    "поиск": ["поисковый"],
    "бд": ["база", "данные"],
    "субд": ["база", "данные"],
}


def damerau_levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    len_a, len_b = len(a), len(b)
    if abs(len_a - len_b) > MAX_EDIT_DISTANCE:
        return MAX_EDIT_DISTANCE + 1

    previous = list(range(len_b + 1))
    before_previous = [0] * (len_b + 1)
    for i in range(1, len_a + 1):
        current = [i] + [0] * len_b
        for j in range(1, len_b + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            current[j] = min(
                current[j - 1] + 1,
                previous[j] + 1,
                previous[j - 1] + cost,
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                current[j] = min(current[j], before_previous[j - 2] + 1)
        before_previous, previous = previous, current
    return previous[len_b]


def suggest(prefix: str) -> list[str]:
    prefix = prefix.strip().lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    if len(prefix) < 2:
        return []
    rows = fetch_all(
        """
        SELECT term FROM terms
        WHERE term LIKE %s ESCAPE '\\'
        ORDER BY df DESC, term
        LIMIT %s
        """,
        (prefix + "%", SUGGEST_LIMIT),
    )
    return [row["term"] for row in rows]


def _vocabulary(length: int) -> list[str]:
    rows = fetch_all(
        """
        SELECT term FROM terms
        WHERE length(term) BETWEEN %s AND %s AND df > 0
        ORDER BY df DESC
        """,
        (max(length - MAX_EDIT_DISTANCE, 1), length + MAX_EDIT_DISTANCE),
    )
    return [row["term"] for row in rows]


def correct_query(query: str) -> tuple[str, list[dict]]:
    corrections: list[dict] = []
    known = {row["term"] for row in fetch_all("SELECT term FROM terms")}
    result_words: list[str] = []

    for word in re.findall(r"[\w-]+|\W+", query, flags=re.UNICODE):
        lemma = lemmatize(word) if word.strip() else ""
        known_word = lemma in known or lemma in ABBREVIATIONS or lemma in THESAURUS
        if not lemma or not is_meaningful(lemma) or known_word:
            result_words.append(word)
            continue

        best, best_distance = None, MAX_EDIT_DISTANCE + 1
        for candidate in _vocabulary(len(lemma)):
            distance = damerau_levenshtein(lemma, candidate)
            if distance < best_distance:
                best, best_distance = candidate, distance
                if distance == 1:
                    break

        if best and best_distance <= MAX_EDIT_DISTANCE:
            corrections.append({"from": word, "to": best, "distance": best_distance})
            result_words.append(best)
        else:
            result_words.append(word)

    return "".join(result_words), corrections


def expand_query(lemmas: list[str]) -> tuple[list[str], list[str]]:
    added: list[str] = []
    expanded = list(lemmas)
    for lemma in lemmas:
        for synonym in THESAURUS.get(lemma, []):
            if synonym not in expanded:
                expanded.append(synonym)
                added.append(synonym)
    return expanded, added


def build_snippet(body: str, query_lemmas: set[str]) -> tuple[str, list[str]]:
    tokens = tokenize(body)
    hits = [token for token in tokens if token.lemma in query_lemmas]
    matched_forms: list[str] = []
    for token in hits:
        if token.surface.lower() not in {form.lower() for form in matched_forms}:
            matched_forms.append(token.surface)

    if hits:
        center = hits[0].start
    else:
        center = 0

    half = SNIPPET_WINDOW // 2
    start = max(center - half, 0)
    end = min(start + SNIPPET_WINDOW, len(body))
    start = max(min(start, max(end - SNIPPET_WINDOW, 0)), 0)

    fragment_tokens = [t for t in hits if start <= t.start < end]
    pieces: list[str] = []
    cursor = start
    for token in fragment_tokens:
        pieces.append(html.escape(body[cursor:token.start]))
        pieces.append(f"<mark>{html.escape(body[token.start:token.end])}</mark>")
        cursor = token.end
    pieces.append(html.escape(body[cursor:end]))

    snippet = "".join(pieces).replace("\n", " ")
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(body) else ""
    return f"{prefix}{snippet}{suffix}", matched_forms


def highlight_document(body: str, query_lemmas: set[str]) -> str:
    if not query_lemmas:
        return html.escape(body)
    pieces: list[str] = []
    cursor = 0
    for token in tokenize(body):
        if token.lemma not in query_lemmas:
            continue
        pieces.append(html.escape(body[cursor:token.start]))
        pieces.append(f"<mark>{html.escape(token.surface)}</mark>")
        cursor = token.end
    pieces.append(html.escape(body[cursor:]))
    return "".join(pieces)


def analyze_query(raw_query: str) -> dict:
    corrected, corrections = correct_query(raw_query)
    lemmas = normalize(corrected)
    expanded, added = expand_query(lemmas)
    return {
        "original": raw_query,
        "corrected": corrected if corrections else raw_query,
        "corrections": corrections,
        "lemmas": lemmas,
        "expanded": expanded,
        "added_synonyms": added,
    }
