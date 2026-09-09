import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'

class StorageService:
    @staticmethod
    def _ensure_data_dir():
        DATA_DIR.mkdir(exist_ok=True)

    @staticmethod
    def save_json(filename, data):
        StorageService._ensure_data_dir()
        with open(DATA_DIR / filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_json(filename, default=None):
        StorageService._ensure_data_dir()
        path = DATA_DIR / filename
        if not path.exists():
            return default
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)