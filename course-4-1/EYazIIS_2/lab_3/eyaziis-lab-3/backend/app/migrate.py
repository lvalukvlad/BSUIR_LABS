import logging

from .config import MIGRATIONS_DIR
from .db import get_cursor, init_pool

log = logging.getLogger(__name__)

SCHEMA_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version    TEXT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT NOW()
)
"""


def run_migrations():
    init_pool()
    done_now = []
    with get_cursor() as cur:
        cur.execute(SCHEMA_TABLE)
        cur.execute("SELECT version FROM schema_migrations")
        already = {row["version"] for row in cur.fetchall()}
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in already:
                continue
            log.info("миграция %s", path.name)
            cur.execute(path.read_text(encoding="utf-8"))
            cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (path.name,))
            done_now.append(path.name)
    return done_now
