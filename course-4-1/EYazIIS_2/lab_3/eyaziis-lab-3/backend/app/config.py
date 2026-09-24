import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "corpus"
MIGRATIONS_DIR = BASE_DIR.parent / "migrations"
EXPORT_DIR = Path(os.getenv("EXPORT_DIR", str(BASE_DIR.parent.parent.parent / "eyazis-report-3" / "png")))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "ips"),
    "user": os.getenv("DB_USER", "ips"),
    "password": os.getenv("DB_PASSWORD", "ips"),
}

SUMMARY_SENTENCES = int(os.getenv("SUMMARY_SENTENCES", "10"))
KEYWORD_LIMIT = 8
PHRASE_MIN_COUNT = 2
