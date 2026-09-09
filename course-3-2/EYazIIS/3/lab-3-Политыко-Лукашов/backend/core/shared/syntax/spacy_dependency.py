"""
Дерево зависимостей через spaCy (UD), с выравниванием к токенам razdel/pymorphy.
При недоступности модели или сбое выравнивания возвращает None — тогда используется прежняя эвристика.
"""

from __future__ import annotations

from typing import Any, Callable

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is False:
        return None
    if _nlp is not None:
        return _nlp
    try:
        import spacy

        _nlp = spacy.load("ru_core_news_sm")
        return _nlp
    except Exception:
        _nlp = False
        return None


def _find_spacy_token(doc, char_start: int, char_end: int):
    """Первый токен spaCy с непустым пересечением отрезка [char_start, char_end)."""
    best = None
    best_ov = -1
    for t in doc:
        if t.is_space:
            continue
        a, b = t.idx, t.idx + len(t.text)
        ov = min(char_end, b) - max(char_start, a)
        if ov > best_ov:
            best_ov = ov
            best = t
    return best if best_ov > 0 else None


def build_flat_dependency_spacy(
    sentence_text: str,
    tokens: list[dict[str, Any]],
    relation_ru: dict[str, str],
    token_text_fn: Callable[[dict[str, Any]], str],
    safe_pos_fn: Callable[[dict[str, Any]], str],
) -> tuple[list[dict[str, Any]], int] | None:
    """
    Возвращает (flat_repr, root_index_0based) в том же формате, что и эвристический билдер,
    или None, если нужен fallback.
    """
    nlp = _get_nlp()
    if not nlp or not sentence_text.strip() or not tokens:
        return None

    from razdel import tokenize

    rtoks = list(tokenize(sentence_text))
    if len(rtoks) != len(tokens):
        return None

    doc = nlp(sentence_text)
    n = len(tokens)

    our_to_spacy: list[int] = []
    for i in range(n):
        cs, ce = rtoks[i].start, rtoks[i].stop
        st = _find_spacy_token(doc, cs, ce)
        if st is None:
            return None
        our_to_spacy.append(st.i)

    if len(our_to_spacy) != len(set(our_to_spacy)):
        return None

    def our_index_for_spacy(si: int) -> int | None:
        for j in range(n):
            if our_to_spacy[j] == si:
                return j
        return None

    root_our: int | None = None
    for i in range(n):
        st = doc[our_to_spacy[i]]
        if st.dep_.lower() == "root" or st.head == st:
            root_our = i
            break
    if root_our is None:
        root_our = 0

    flat_repr: list[dict[str, Any]] = []
    for i in range(n):
        td = tokens[i]
        st = doc[our_to_spacy[i]]
        rel = (st.dep_ or "dep").lower()

        if st.head == st or rel == "root":
            head = 0
            relation = "root"
        else:
            hj = our_index_for_spacy(st.head.i)
            if hj is None:
                hj = root_our
            head = hj + 1
            relation = rel

        relation_ru_label = relation_ru.get(relation)
        if relation_ru_label is None:
            relation_ru_label = relation_ru.get(
                relation.split(":", 1)[0],
                td.get("syntax_role_name", "") or relation,
            )

        flat_repr.append(
            {
                "id": i + 1,
                "token": token_text_fn(td),
                "lemma": td.get("lemma", ""),
                "pos": safe_pos_fn(td),
                "pos_name": td.get("pos_name", ""),
                "head": head,
                "relation": relation,
                "relation_ru": relation_ru_label,
                "syntax_role": td.get("syntax_role", ""),
                "syntax_role_name": td.get("syntax_role_name", ""),
                "case": td.get("case", ""),
                "case_name": td.get("case_name", ""),
                "number": td.get("number", ""),
                "number_name": td.get("number_name", ""),
                "gender": td.get("gender", ""),
                "gender_name": td.get("gender_name", ""),
            }
        )

    return flat_repr, root_our
