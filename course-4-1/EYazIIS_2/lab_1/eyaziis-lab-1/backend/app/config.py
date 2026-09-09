import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "corpus"
MIGRATIONS_DIR = BASE_DIR.parent / "migrations"
EXPORT_DIR = Path(os.getenv("EXPORT_DIR", "/out/png"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "ips"),
    "user": os.getenv("DB_USER", "ips"),
    "password": os.getenv("DB_PASSWORD", "ips"),
}

BM25_K1 = float(os.getenv("BM25_K1", "1.2"))
BM25_B = float(os.getenv("BM25_B", "0.75"))

PRF_TOP_R = int(os.getenv("PRF_TOP_R", "5"))
PRF_ENABLED_BY_DEFAULT = os.getenv("PRF_ENABLED", "0") == "1"

SNIPPET_WINDOW = 320
DEFAULT_TOP_K = 10

SCORE_CUTOFF_RATIO = float(os.getenv("SCORE_CUTOFF_RATIO", "0.25"))
