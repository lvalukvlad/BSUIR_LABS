import time

from psycopg2.extras import Json, execute_values

from .db import execute, fetch_all, fetch_one, get_cursor
from .summarizer import parse_document, summarize


def insert_document(title, body, language, domain, source_file=None):
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents (title, body, language, domain, source_file)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source_file) DO UPDATE
                SET title = EXCLUDED.title,
                    body = EXCLUDED.body,
                    language = EXCLUDED.language,
                    domain = EXCLUDED.domain
            RETURNING id
            """,
            (title, body, language, domain, source_file),
        )
        return cur.fetchone()["id"]


def add_document(title, body, language, domain, source_file=None):
    doc_id = insert_document(title, body, language, domain, source_file)
    rebuild_all()
    return doc_id


def delete_document(doc_id):
    with get_cursor() as cur:
        cur.execute("DELETE FROM documents WHERE id = %s RETURNING id", (doc_id,))
        ok = cur.fetchone() is not None
    if ok:
        rebuild_all()
    return ok


def rebuild_all():
    rows = fetch_all("SELECT id, title, body, language, domain FROM documents ORDER BY id")
    if not rows:
        execute("DELETE FROM doc_terms")
        execute("DELETE FROM global_terms")
        return

    df = {}
    for row in rows:
        words = parse_document(row["body"], row["language"])["vocabulary"]
        for t in words:
            df[t] = df.get(t, 0) + 1
    n = len(rows)

    execute("DELETE FROM doc_terms")
    execute("DELETE FROM global_terms")
    if df:
        with get_cursor() as cur:
            execute_values(cur, "INSERT INTO global_terms (term, df) VALUES %s", list(df.items()))

    for row in rows:
        t0 = time.perf_counter()
        res = summarize(row["body"], row["language"], row["title"], row["domain"], n, df)
        ms = round((time.perf_counter() - t0) * 1000, 2)
        execute(
            """
            UPDATE documents
            SET char_len = %s,
                summary_classic = %s,
                keywords_json = %s,
                network_json = %s,
                selected_json = %s,
                sentences_json = %s,
                baseline_classic = %s,
                baseline_selected = %s,
                elapsed_ms = %s
            WHERE id = %s
            """,
            (
                res["char_len"],
                res["classic"],
                Json(res["keywords"]),
                Json(res["network"]),
                Json(res["selected"]),
                Json(res["sentences"]),
                res["baseline"],
                Json(res["baseline_selected"]),
                ms,
                row["id"],
            ),
        )
        if res["terms"]:
            with get_cursor() as cur:
                execute_values(
                    cur,
                    "INSERT INTO doc_terms (doc_id, term, tf, weight) VALUES %s",
                    [(row["id"], x["term"], x["tf"], x["weight"]) for x in res["terms"]],
                )


def list_documents():
    return fetch_all(
        """
        SELECT id, title, language, domain, source_file, char_len, elapsed_ms,
               CASE WHEN source_file LIKE '%%.txt' AND source_file NOT LIKE 'upload%%'
                    THEN 'etalon' ELSE 'upload' END AS source_kind,
               to_char(created_at, 'DD.MM.YYYY HH24:MI') AS created_at
        FROM documents
        ORDER BY id
        """
    )


def get_document(doc_id):
    return fetch_one(
        """
        SELECT id, title, body, language, domain, source_file, char_len,
               summary_classic, keywords_json, network_json, selected_json,
               sentences_json, baseline_classic, baseline_selected, elapsed_ms,
               CASE WHEN source_file LIKE '%%.txt' AND source_file NOT LIKE 'upload%%'
                    THEN 'etalon' ELSE 'upload' END AS source_kind,
               to_char(created_at, 'DD.MM.YYYY HH24:MI') AS created_at
        FROM documents WHERE id = %s
        """,
        (doc_id,),
    )
