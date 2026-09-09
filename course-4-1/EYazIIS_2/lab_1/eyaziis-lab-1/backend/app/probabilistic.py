import math
from collections import Counter
from dataclasses import dataclass, field

from .config import BM25_B, BM25_K1, PRF_TOP_R
from .db import fetch_all, fetch_one

MIN_WEIGHT = 1e-6


@dataclass
class QueryTerm:

    term_id: int
    term: str
    df: int
    qtf: int
    weight: float = 0.0


@dataclass
class ScoredDocument:
    doc_id: int
    score: float
    matched: list[str] = field(default_factory=list)


def collection_size() -> tuple[float, float]:
    row = fetch_one(
        """
        SELECT COUNT(*)::float AS n,
               GREATEST(COALESCE(AVG(doc_len), 1), 1)::float AS avgdl
        FROM documents
        """
    )
    return row["n"], row["avgdl"]


def rsj_weight(n_docs: float, df: int) -> float:
    return math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))


def rsj_weight_with_feedback(n_docs: float, df: int, rel_total: int, rel_with_term: int) -> float:
    r = float(rel_with_term)
    big_r = float(rel_total)
    numerator = (r + 0.5) / (big_r - r + 0.5)
    denominator = (df - r + 0.5) / (n_docs - df - big_r + r + 0.5)
    return max(math.log(numerator / denominator), MIN_WEIGHT)


def resolve_query_terms(lemmas: list[str]) -> list[QueryTerm]:
    if not lemmas:
        return []
    counts = Counter(lemmas)
    rows = fetch_all(
        "SELECT id, term, df FROM terms WHERE term = ANY(%s)", (list(counts),)
    )
    n_docs, _ = collection_size()
    return [
        QueryTerm(
            term_id=row["id"],
            term=row["term"],
            df=row["df"],
            qtf=counts[row["term"]],
            weight=rsj_weight(n_docs, row["df"]) * counts[row["term"]],
        )
        for row in rows
    ]


def _score(terms: list[QueryTerm], limit: int) -> list[ScoredDocument]:
    if not terms:
        return []
    rows = fetch_all(
        """
        WITH stats AS (
            SELECT GREATEST(COALESCE(AVG(doc_len), 1), 1)::float AS avgdl FROM documents
        ),
        qt AS (
            SELECT * FROM unnest(%(ids)s::int[], %(weights)s::float[]) AS q(term_id, w)
        )
        SELECT p.doc_id,
               SUM(
                   qt.w * (p.tf * (%(k1)s + 1.0))
                   / (p.tf + %(k1)s * (1.0 - %(b)s + %(b)s * d.doc_len / stats.avgdl))
               ) AS score,
               array_agg(t.term ORDER BY t.term) AS matched
        FROM postings p
        JOIN qt ON qt.term_id = p.term_id
        JOIN terms t ON t.id = p.term_id
        JOIN documents d ON d.id = p.doc_id
        CROSS JOIN stats
        GROUP BY p.doc_id
        ORDER BY score DESC
        LIMIT %(limit)s
        """,
        {
            "ids": [t.term_id for t in terms],
            "weights": [t.weight for t in terms],
            "k1": BM25_K1,
            "b": BM25_B,
            "limit": limit,
        },
    )
    return [
        ScoredDocument(doc_id=row["doc_id"], score=float(row["score"]), matched=row["matched"])
        for row in rows
    ]


def _apply_pseudo_relevance_feedback(
    terms: list[QueryTerm], first_pass: list[ScoredDocument]
) -> list[QueryTerm]:
    top_docs = [doc.doc_id for doc in first_pass[:PRF_TOP_R]]
    if len(top_docs) < 2:
        return terms

    n_docs, _ = collection_size()
    rows = fetch_all(
        """
        SELECT term_id, COUNT(*)::int AS hits
        FROM postings
        WHERE doc_id = ANY(%s) AND term_id = ANY(%s)
        GROUP BY term_id
        """,
        (top_docs, [t.term_id for t in terms]),
    )
    hits = {row["term_id"]: row["hits"] for row in rows}

    updated: list[QueryTerm] = []
    for term in terms:
        weight = rsj_weight_with_feedback(
            n_docs, term.df, len(top_docs), hits.get(term.term_id, 0)
        )
        updated.append(
            QueryTerm(
                term_id=term.term_id,
                term=term.term,
                df=term.df,
                qtf=term.qtf,
                weight=weight * term.qtf,
            )
        )
    return updated


def search(lemmas: list[str], limit: int = 10, use_prf: bool = True) -> tuple[list[ScoredDocument], list[QueryTerm]]:
    terms = resolve_query_terms(lemmas)
    if not terms:
        return [], []

    first_pass = _score(terms, limit)
    if not use_prf or not first_pass:
        return first_pass, terms

    refined = _apply_pseudo_relevance_feedback(terms, first_pass)
    return _score(refined, limit), refined


def search_tfidf(lemmas: list[str], limit: int = 10) -> list[ScoredDocument]:
    if not lemmas:
        return []
    rows = fetch_all(
        """
        WITH stats AS (SELECT COUNT(*)::float AS n FROM documents),
        qt AS (
            SELECT t.id AS term_id, ln(stats.n / GREATEST(t.df, 1)) + 1.0 AS idf
            FROM terms t CROSS JOIN stats
            WHERE t.term = ANY(%(lemmas)s)
        ),
        doc_weights AS (
            SELECT p.doc_id, p.term_id,
                   (1.0 + ln(p.tf)) * (ln(stats.n / GREATEST(t.df, 1)) + 1.0) AS w
            FROM postings p JOIN terms t ON t.id = p.term_id CROSS JOIN stats
        ),
        norms AS (
            SELECT doc_id, sqrt(SUM(w * w)) AS norm FROM doc_weights GROUP BY doc_id
        )
        SELECT dw.doc_id,
               SUM(dw.w * qt.idf) / (MAX(n.norm) * sqrt(SUM(qt.idf * qt.idf))) AS score,
               array_agg(t.term ORDER BY t.term) AS matched
        FROM doc_weights dw
        JOIN qt ON qt.term_id = dw.term_id
        JOIN terms t ON t.id = dw.term_id
        JOIN norms n ON n.doc_id = dw.doc_id
        GROUP BY dw.doc_id
        ORDER BY score DESC
        LIMIT %(limit)s
        """,
        {"lemmas": list(set(lemmas)), "limit": limit},
    )
    return [
        ScoredDocument(doc_id=row["doc_id"], score=float(row["score"]), matched=row["matched"])
        for row in rows
    ]
