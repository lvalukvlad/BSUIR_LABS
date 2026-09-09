from pathlib import Path
from typing import List

APP_TITLE = "NLP Dictionary Lab"
APP_VERSION = "1.0"
APP_DESCRIPTION = "Автоматизированная система формирования словаря естественного языка"

HOST = "127.0.0.1"
PORT = 8000
DEBUG = True

# Пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
LOGS_DIR = DATA_DIR / "logs"
DICTIONARY_PATH = DATA_DIR / "dictionary.json"

# Создаём директории
for dir_path in [DATA_DIR, UPLOADS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TOKENS = 100000

SUPPORTED_FORMATS = {
    'txt': ['txt', 'text'],
    'rtf': ['rtf']
}

ALLOWED_ORIGINS = ["*"]