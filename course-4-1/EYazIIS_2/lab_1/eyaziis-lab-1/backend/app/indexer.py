"""Индексатор: построение и поддержка инвертированного индекса коллекции."""
import logging
from collections import Counter

import psycopg2.extras

from .db import get_cursor
from .text_processing import normalize

log = logging.getLogger(__name__)

SUMMARY_LENGTH = 260


def make_summary(body: str) -> str:
    flat = " ".join(body.split())
    if len(flat) <= SUMMARY_LENGTH:
        return flat
    return flat[:SUMMARY_LENGTH].rsplit(" ", 1)[0] + "..."


def index_document(title: str, body: str, source_file: str | None = None) -> int:
    """Добавляет документ в коллекцию и обновляет инвертированный индекс."""
    lemmas = normalize(body + " " + title)
    frequencies = Counter(lemmas)

    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents (title, body, summary, source_file, doc_len)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source_file) DO UPDATE
                SET title = EXCLUDED.title,
                    body = EXCLUDED.body,
                    summary = EXCLUDED.summary,
                    doc_len = EXCLUDED.doc_len
            RETURNING id
            """,
            (title, body, make_summary(body), source_file, len(lemmas)),
        )
        doc_id = cur.fetchone()["id"]

        cur.execute("DELETE FROM postings WHERE doc_id = %s", (doc_id,))

        if frequencies:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO terms (term, df) VALUES %s
                ON CONFLICT (term) DO NOTHING
                """,
                [(term, 0) for term in frequencies],
            )
            cur.execute(
                "SELECT id, term FROM terms WHERE term = ANY(%s)",
                (list(frequencies),),
            )
            term_ids = {row["term"]: row["id"] for row in cur.fetchall()}
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO postings (term_id, doc_id, tf) VALUES %s",
                [(term_ids[term], doc_id, tf) for term, tf in frequencies.items()],
            )

    refresh_document_frequencies()
    return doc_id


def delete_document(doc_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute("DELETE FROM documents WHERE id = %s RETURNING id", (doc_id,))
        deleted = cur.fetchone() is not None
    if deleted:
        refresh_document_frequencies()
    return deleted


def refresh_document_frequencies() -> None:
    """Пересчитывает документные частоты терминов и удаляет осиротевшие термины."""
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE terms t
            SET df = COALESCE(sub.cnt, 0)
            FROM (
                SELECT term_id, COUNT(*) AS cnt FROM postings GROUP BY term_id
            ) AS sub
            WHERE t.id = sub.term_id AND t.df IS DISTINCT FROM sub.cnt
            """
        )
        cur.execute(
            "DELETE FROM terms WHERE id NOT IN (SELECT DISTINCT term_id FROM postings)"
        )


def collection_stats() -> dict:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)::int AS documents,
                   COALESCE(AVG(doc_len), 0)::float AS avg_doc_len,
                   COALESCE(SUM(doc_len), 0)::int AS total_tokens
            FROM documents
            """
        )
        stats = dict(cur.fetchone())
        cur.execute("SELECT COUNT(*)::int AS terms FROM terms")
        stats.update(cur.fetchone())
        cur.execute("SELECT COUNT(*)::int AS postings FROM postings")
        stats.update(cur.fetchone())
        cur.execute("SELECT COUNT(*)::int AS searches FROM search_logs")
        stats.update(cur.fetchone())
    return stats


def list_documents() -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, title, summary, source_file, doc_len,
                   to_char(created_at, 'DD.MM.YYYY HH24:MI') AS created_at
            FROM documents
            ORDER BY id
            """
        )
        return [dict(row) for row in cur.fetchall()]


def get_document(doc_id: int) -> dict | None:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, title, body, summary, source_file, doc_len,
                   to_char(created_at, 'DD.MM.YYYY HH24:MI') AS created_at
            FROM documents WHERE id = %s
            """,
            (doc_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def top_terms(doc_id: int, limit: int = 10) -> list[dict]:
    """Ключевые термины документа по убыванию веса Робертсона -- Спарк Джонс."""
    with get_cursor() as cur:
        cur.execute(
            """
            WITH stats AS (SELECT COUNT(*)::float AS n FROM documents)
            SELECT t.term,
                   p.tf,
                   p.tf * ln(1 + (stats.n - t.df + 0.5) / (t.df + 0.5)) AS weight
            FROM postings p
            JOIN terms t ON t.id = p.term_id
            CROSS JOIN stats
            WHERE p.doc_id = %s
            ORDER BY weight DESC
            LIMIT %s
            """,
            (doc_id, limit),
        )
        return [dict(row) for row in cur.fetchall()]
