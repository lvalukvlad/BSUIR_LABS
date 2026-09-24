import json
import logging

from .config import CORPUS_DIR
from .db import fetch_one
from .document_loader import split_title
from .indexer import insert_document, rebuild_all

log = logging.getLogger(__name__)


def initialize():
    manifest = json.loads((CORPUS_DIR / "manifest.json").read_text(encoding="utf-8"))
    n = 0
    for item in manifest:
        raw = (CORPUS_DIR / item["file"]).read_text(encoding="utf-8")
        title, body = split_title(raw)
        insert_document(
            title=title,
            body=body,
            language=item["language"],
            domain=item["domain"],
            source_file=item["file"],
        )
        n += 1
    rebuild_all()
    row = fetch_one("SELECT COUNT(*)::int AS cnt FROM documents")
    total = row["cnt"] if row else n
    log.info("загружено эталонов %s, всего %s", n, total)
    return {"documents_loaded": n, "documents_total": total}
