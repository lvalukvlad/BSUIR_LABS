import json
import logging

from .config import CORPUS_DIR
from .db import get_cursor
from .indexer import index_document

log = logging.getLogger(__name__)


def _split_title(raw: str) -> tuple[str, str]:
    lines = raw.splitlines()
    title_idx = next((i for i, line in enumerate(lines) if line.strip()), None)
    if title_idx is None:
        return "Без названия", raw
    title = lines[title_idx].strip()
    body = "\n".join(lines[title_idx + 1:]).strip()
    return title, body or raw


def load_corpus(force: bool = False) -> int:
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*)::int AS cnt FROM documents")
        existing = cur.fetchone()["cnt"]

    if existing and not force:
        log.info("Коллекция уже загружена: %s документов", existing)
        return 0

    loaded = 0
    for path in sorted(CORPUS_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        title, body = _split_title(raw)
        index_document(title=title, body=body, source_file=path.name)
        loaded += 1

    log.info("Загружено документов: %s", loaded)
    return loaded


def load_qrels() -> int:
    path = CORPUS_DIR / "qrels.json"
    if not path.exists():
        return 0

    payload = json.loads(path.read_text(encoding="utf-8"))
    loaded = 0
    with get_cursor() as cur:
        for item in payload["queries"]:
            cur.execute(
                """
                INSERT INTO eval_queries (code, query, comment)
                VALUES (%s, %s, %s)
                ON CONFLICT (code) DO UPDATE
                    SET query = EXCLUDED.query, comment = EXCLUDED.comment
                RETURNING id
                """,
                (item["code"], item["query"], item.get("comment", "")),
            )
            query_id = cur.fetchone()["id"]
            cur.execute("DELETE FROM eval_qrels WHERE query_id = %s", (query_id,))
            for source_file in item["relevant"]:
                cur.execute(
                    """
                    INSERT INTO eval_qrels (query_id, source_file, relevance)
                    VALUES (%s, %s, 1)
                    ON CONFLICT DO NOTHING
                    """,
                    (query_id, source_file),
                )
            loaded += 1
    log.info("Загружено эталонных запросов: %s", loaded)
    return loaded


def initialize(force: bool = False) -> dict:
    documents = load_corpus(force=force)
    queries = load_qrels()
    return {"documents_loaded": documents, "queries_loaded": queries}
