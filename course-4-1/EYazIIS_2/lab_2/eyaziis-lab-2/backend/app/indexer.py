from psycopg2.extras import Json

from .db import get_cursor


def source_kind(source_file: str | None) -> str:
    name = (source_file or "").lower()
    if name.startswith("eval_") or name.startswith("eval/"):
        return "etalon"
    return "upload"


def _with_source(document: dict) -> dict:
    document["source_kind"] = source_kind(document.get("source_file"))
    return document


def save_recognition_result(
    doc_id: int,
    method: str,
    language: str,
    confidence: float,
    result_json,
) -> None:
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO recognition_results (doc_id, method, language, confidence, result_json)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (doc_id, method, language, confidence, Json(result_json)),
        )


def save_document(
    title: str,
    body: str,
    source_file: str | None,
    detected_language: str,
    result_json,
) -> int:
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents (title, body, source_file, doc_len, detected_language, result_json)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_file) DO UPDATE
                SET title = EXCLUDED.title,
                    body = EXCLUDED.body,
                    doc_len = EXCLUDED.doc_len,
                    detected_language = EXCLUDED.detected_language,
                    result_json = EXCLUDED.result_json
            RETURNING id
            """,
            (
                title,
                body,
                source_file,
                len(body.split()),
                detected_language,
                Json(result_json),
            ),
        )
        doc_id = cur.fetchone()["id"]
        cur.execute("DELETE FROM recognition_results WHERE doc_id = %s", (doc_id,))
        return doc_id


def get_documents() -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, title, source_file, doc_len, detected_language, result_json,
                   to_char(created_at, 'DD.MM.YYYY HH24:MI') AS created_at
            FROM documents
            ORDER BY created_at DESC, id DESC
            """
        )
        return [_with_source(dict(row)) for row in cur.fetchall()]


def get_document(doc_id: int) -> dict | None:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, title, body, source_file, doc_len, detected_language, result_json,
                   to_char(created_at, 'DD.MM.YYYY HH24:MI') AS created_at
            FROM documents
            WHERE id = %s
            """,
            (doc_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        document = dict(row)
        cur.execute(
            """
            SELECT method, language, confidence, result_json,
                   to_char(created_at, 'DD.MM.YYYY HH24:MI') AS created_at
            FROM recognition_results
            WHERE doc_id = %s
            ORDER BY id
            """,
            (doc_id,),
        )
        document["methods"] = [dict(item) for item in cur.fetchall()]
        return _with_source(document)


def delete_document(doc_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute("DELETE FROM recognition_results WHERE doc_id = %s", (doc_id,))
        cur.execute("DELETE FROM documents WHERE id = %s RETURNING id", (doc_id,))
        return cur.fetchone() is not None


def collection_stats() -> dict:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)::int AS documents,
                   COALESCE(AVG(doc_len), 0)::float AS avg_doc_len
            FROM documents
            """
        )
        stats = dict(cur.fetchone())
        cur.execute("SELECT COUNT(*)::int AS results FROM recognition_results")
        stats["results"] = cur.fetchone()["results"]
        for language in ["русский", "немецкий"]:
            cur.execute(
                "SELECT COUNT(*)::int AS cnt FROM documents WHERE detected_language LIKE %s",
                (f"%{language}%",),
            )
            stats[f"{language}_count"] = cur.fetchone()["cnt"]
    return stats
