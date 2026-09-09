from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from core.dialog.nlp_utils import corpus_normalize

_STORE: dict[str, Any] = {}


def corpus_directory() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "data" / "corpus"


def _split_chunks(text: str, title: str, filename: str) -> tuple[list[str], list[dict]]:
    chunks = []
    meta = []
    for raw in text.split("\n\n"):
        block = raw.strip()
        if len(block) < 50:
            continue
        chunks.append(block)
        meta.append({"file": filename, "section_title": title, "length": len(block)})
    return chunks, meta


def load_all_chunks() -> tuple[list[str], list[dict]]:
    root = corpus_directory()
    all_chunks: list[str] = []
    all_meta: list[dict] = []
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        return [], []
    for path in sorted(root.glob("*.txt")):
        title = path.stem.replace("_", " ")
        body = path.read_text(encoding="utf-8")
        ch, mt = _split_chunks(body, title, path.name)
        all_chunks.extend(ch)
        all_meta.extend(mt)
    return all_chunks, all_meta


def build_corpus_index() -> None:
    global _STORE
    chunks, meta = load_all_chunks()
    if not chunks:
        _STORE = {
            "ready": True,
            "vectorizer": None,
            "matrix": None,
            "chunks": [],
            "meta": [],
        }
        return
    norm = [corpus_normalize(c) for c in chunks]
    vectorizer = TfidfVectorizer(
        max_features=16000,
        ngram_range=(1, 2),
        min_df=1,
    )
    matrix = vectorizer.fit_transform(norm)
    _STORE = {
        "ready": True,
        "vectorizer": vectorizer,
        "matrix": matrix,
        "chunks": chunks,
        "meta": meta,
    }


def index_status() -> dict:
    if not _STORE.get("ready"):
        build_corpus_index()
    return {
        "chunk_count": len(_STORE.get("chunks") or []),
        "indexed": _STORE.get("vectorizer") is not None,
        "corpus_dir": str(corpus_directory()),
    }


def search_corpus(
    query: str,
    top_k: int = 3,
    min_score: float = 0.06,
) -> list[dict]:
    if not _STORE.get("ready"):
        build_corpus_index()
    vec = _STORE.get("vectorizer")
    matrix = _STORE.get("matrix")
    chunks = _STORE.get("chunks") or []
    meta = _STORE.get("meta") or []
    if not vec or matrix is None or not chunks:
        return []
    qv = vec.transform([corpus_normalize(query)])
    sims = cosine_similarity(qv, matrix)[0]
    idx = np.argsort(sims)[::-1][: max(top_k * 4, top_k)]
    out = []
    seen_text = set()
    for i in idx:
        score = float(sims[i])
        if score < min_score:
            continue
        text = chunks[i]
        if text in seen_text:
            continue
        seen_text.add(text)
        m = meta[i] if i < len(meta) else {}
        out.append(
            {
                "text": text,
                "score": round(score, 4),
                "meta": m,
            }
        )
        if len(out) >= top_k:
            break
    return out
