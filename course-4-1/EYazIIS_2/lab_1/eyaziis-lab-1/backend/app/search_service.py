"""Оркестрация поиска: разбор запроса, ранжирование, формирование выдачи."""
import time

from . import probabilistic
from .config import DEFAULT_TOP_K, SCORE_CUTOFF_RATIO
from .db import execute, fetch_all
from .query_assistant import analyze_query, build_snippet


def _cut_off_noise(scored: list) -> list:
    """Отбрасывает документы, чья оценка много ниже оценки лучшего документа."""
    if not scored:
        return []
    best = max(doc.score for doc in scored)
    if best <= 0:
        return []
    threshold = best * SCORE_CUTOFF_RATIO
    return [doc for doc in scored if doc.score >= threshold]


def _load_documents(doc_ids: list[int]) -> dict[int, dict]:
    if not doc_ids:
        return {}
    rows = fetch_all(
        """
        SELECT id, title, body, source_file, doc_len,
               to_char(created_at, 'DD.MM.YYYY') AS created_at,
               created_at AS created_raw
        FROM documents WHERE id = ANY(%s)
        """,
        (doc_ids,),
    )
    return {row["id"]: row for row in rows}


def search(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    use_prf: bool = True,
    model: str = "bm25",
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    """Выполняет поиск и возвращает готовую поисковую выдачу с сниппетами."""
    started = time.perf_counter()
    analysis = analyze_query(query)
    lemmas = analysis["expanded"]

    if model == "tfidf":
        scored = probabilistic.search_tfidf(lemmas, limit=top_k * 3)
        query_terms = []
    else:
        scored, query_terms = probabilistic.search(lemmas, limit=top_k * 3, use_prf=use_prf)

    scored = _cut_off_noise(scored)
    documents = _load_documents([doc.doc_id for doc in scored])
    query_lemma_set = set(lemmas)

    results = []
    for position, doc in enumerate(scored, start=1):
        meta = documents.get(doc.doc_id)
        if meta is None or doc.score <= 0:
            continue
        if date_from and str(meta["created_raw"].date()) < date_from:
            continue
        if date_to and str(meta["created_raw"].date()) > date_to:
            continue

        snippet, matched_forms = build_snippet(meta["body"], query_lemma_set)
        results.append(
            {
                "document_id": doc.doc_id,
                "title": meta["title"],
                "snippet": snippet,
                "rank": round(doc.score, 4),
                "date": meta["created_at"],
                "source_file": meta["source_file"],
                "doc_len": meta["doc_len"],
                "matched_terms": doc.matched,
                "matched_words": matched_forms,
                "position": position,
            }
        )
        if len(results) >= top_k:
            break

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    execute(
        """
        INSERT INTO search_logs (query, normalized, results_count, elapsed_ms)
        VALUES (%s, %s, %s, %s)
        """,
        (query, " ".join(analysis["lemmas"]), len(results), elapsed_ms),
    )

    return {
        "query": query,
        "model": model,
        "prf_enabled": use_prf and model == "bm25",
        "analysis": analysis,
        "term_weights": [
            {"term": t.term, "df": t.df, "weight": round(t.weight, 4)}
            for t in query_terms
        ],
        "elapsed_ms": elapsed_ms,
        "total": len(results),
        "results": results,
    }


def retrieve_ids(query: str, top_k: int, model: str = "bm25", use_prf: bool = True) -> list[int]:
    """Возвращает только идентификаторы выдачи -- используется модулем оценки."""
    analysis = analyze_query(query)
    lemmas = analysis["expanded"]
    if model == "tfidf":
        scored = probabilistic.search_tfidf(lemmas, limit=top_k)
    else:
        scored, _ = probabilistic.search(lemmas, limit=top_k, use_prf=use_prf)
    return [doc.doc_id for doc in _cut_off_noise(scored)]
