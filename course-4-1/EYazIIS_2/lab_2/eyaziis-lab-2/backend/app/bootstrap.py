import json
import logging

from .config import CORPUS_DIR, MODEL_PATH
from .db import execute, fetch_all, get_cursor, save_profiles
from .indexer import save_document, save_recognition_result
from .language_model import (
    NeuralNetworkRecognizer,
    build_all_profiles,
    recognize_language,
    summarize_recognition,
)

log = logging.getLogger(__name__)

_runtime: dict | None = None


def reset_runtime() -> None:
    global _runtime
    _runtime = None


def train_models(texts: dict[str, list[str]]) -> NeuralNetworkRecognizer:
    nn = NeuralNetworkRecognizer()
    all_texts: list[str] = []
    all_labels: list[str] = []
    for language, language_texts in texts.items():
        all_texts.extend(language_texts)
        all_labels.extend([language] * len(language_texts))
    if len(set(all_labels)) < 2:
        log.warning("Недостаточно данных для обучения нейросети")
        return nn
    nn.train(all_texts, all_labels)
    nn.save(MODEL_PATH)
    log.info("Нейросеть обучена и сохранена в %s", MODEL_PATH)
    return nn


def load_training_corpus(force: bool = False) -> dict[str, list[str]]:
    texts: dict[str, list[str]] = {}
    with get_cursor() as cur:
        if force:
            cur.execute("DELETE FROM training_texts")
        cur.execute("SELECT language, text FROM training_texts ORDER BY id")
        rows = cur.fetchall()

    if rows and not force:
        for row in rows:
            texts.setdefault(row["language"], []).append(row["text"])
        log.info("Тренировочная коллекция загружена из БД: %s", {key: len(value) for key, value in texts.items()})
        return texts

    train_dir = CORPUS_DIR / "train"
    for language in ["русский", "немецкий"]:
        language_dir = train_dir / language
        if not language_dir.exists():
            continue
        language_texts = []
        for path in sorted(language_dir.glob("*.txt")):
            text = path.read_text(encoding="utf-8")
            language_texts.append(text)
            with get_cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO training_texts (language, text, source_file)
                    VALUES (%s, %s, %s)
                    """,
                    (language, text, f"{language}/{path.name}"),
                )
        texts[language] = language_texts
        log.info("Загружено тренировочных текстов для %s: %d", language, len(language_texts))
    return texts


def load_qrels() -> int:
    path = CORPUS_DIR / "qrels.json"
    if not path.exists():
        return 0
    payload = json.loads(path.read_text(encoding="utf-8"))
    loaded = 0
    with get_cursor() as cur:
        for item in payload.get("queries", []):
            cur.execute(
                """
                INSERT INTO eval_queries (code, query, text, relevant)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (code) DO UPDATE
                    SET query = EXCLUDED.query,
                        text = EXCLUDED.text,
                        relevant = EXCLUDED.relevant
                """,
                (
                    item["code"],
                    item["query"],
                    item.get("text", ""),
                    item.get("relevant") or [],
                ),
            )
            loaded += 1
    log.info("Загружено эталонных запросов: %s", loaded)
    return loaded


def load_profiles() -> dict[str, dict] | None:
    rows = fetch_all("SELECT language, method, lexeme, frequency FROM language_profiles")
    if not rows:
        return None
    profiles: dict[str, dict] = {}
    for row in rows:
        language = row["language"]
        method = row["method"]
        profiles.setdefault(language, {}).setdefault(method, {})[row["lexeme"]] = row["frequency"]
    log.info("Профили загружены из БД: %s", {key: list(value) for key, value in profiles.items()})
    return profiles


def get_runtime(force: bool = False) -> dict:
    global _runtime
    if _runtime is not None and not force:
        return _runtime

    texts = load_training_corpus()
    profiles = None if force else load_profiles()
    nn = NeuralNetworkRecognizer()
    loaded = False if force else nn.load(MODEL_PATH)

    if texts and (profiles is None or not loaded):
        if not loaded:
            nn = train_models(texts)
        if profiles is None:
            execute("DELETE FROM language_profiles")
            profiles = build_all_profiles(texts)
            save_profiles(profiles)

    if profiles is None:
        profiles = {}
    _runtime = {"profiles": profiles, "nn": nn, "texts": texts}
    return _runtime


def _index_test_collection(force: bool = False) -> int:
    runtime = get_runtime()
    rows = fetch_all("SELECT code, query, text, relevant FROM eval_queries ORDER BY code")
    indexed = 0
    for row in rows:
        text = row["text"]
        if not text.strip():
            continue
        results = recognize_language(text, runtime["profiles"], runtime["nn"])
        chosen = summarize_recognition(results)
        gold = (row["relevant"] or ["unknown"])[0]
        doc_id = save_document(
            title=f"{row['code']} · {row['query']}",
            body=text,
            source_file=f"eval_{row['code']}.txt",
            detected_language=chosen.get("language") or "unknown",
            result_json=results,
        )
        for method, payload in results.items():
            if not isinstance(payload, dict) or "method" not in payload:
                continue
            save_recognition_result(
                doc_id,
                method,
                payload.get("language") or gold,
                float(payload.get("confidence") or 0.0),
                payload,
            )
        indexed += 1
    log.info("В тестовую коллекцию добавлено документов: %s", indexed)
    return indexed


def initialize(force: bool = False) -> dict:
    if force:
        reset_runtime()
        execute("DELETE FROM recognition_results")
        execute("DELETE FROM documents")
        execute("DELETE FROM language_profiles")
        execute("DELETE FROM training_texts")

    texts = load_training_corpus(force=force)
    queries = load_qrels()
    runtime = get_runtime(force=force)
    indexed = _index_test_collection(force=force)
    return {
        "training_docs_loaded": sum(len(value) for value in texts.values()),
        "queries_loaded": queries,
        "test_docs_indexed": indexed,
        "languages": list(runtime["profiles"]),
    }
