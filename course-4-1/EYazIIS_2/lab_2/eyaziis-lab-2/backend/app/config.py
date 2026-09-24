import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "corpus"
MIGRATIONS_DIR = BASE_DIR.parent / "migrations"
EXPORT_DIR = Path(os.getenv("EXPORT_DIR", "/out/png"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(BASE_DIR / "model" / "language_classifier.pkl")))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "ips"),
    "user": os.getenv("DB_USER", "ips"),
    "password": os.getenv("DB_PASSWORD", "ips"),
}

LANGUAGES = ["русский", "немецкий"]

MIN_LEXEME_LEN = 5
MIN_OCCURRENCES = 3

TOP_WORDS_COUNT = 50

N_GRAM_MIN = 1
N_GRAM_MAX = 5
MIN_NGRAM_DF = 2

MLP_HIDDEN_LAYERS = (128, 64)
MLP_MAX_ITER = 500
MLP_RANDOM_STATE = 42

UNSEEN_PROB = 1e-8
LANGUAGE_SHARE_THRESHOLD = 0.15

SCORE_CUTOFF_RATIO = 0.25
DEFAULT_TOP_K = 10
