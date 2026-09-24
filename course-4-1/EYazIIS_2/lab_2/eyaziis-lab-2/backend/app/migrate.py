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


def run_migrations() -> list[str]:
    init_pool()
    applied: list[str] = []
    with get_cursor() as cur:
        cur.execute(SCHEMA_TABLE)
        cur.execute("SELECT version FROM schema_migrations")
        done = {row["version"] for row in cur.fetchall()}

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in done:
                continue
            log.info("Применяется миграция %s", path.name)
            cur.execute(path.read_text(encoding="utf-8"))
            cur.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)", (path.name,)
            )
            applied.append(path.name)
    return applied


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    names = run_migrations()
    print("Применено миграций:", len(names))
