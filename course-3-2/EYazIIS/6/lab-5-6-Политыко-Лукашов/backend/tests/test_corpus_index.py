from core.corpus.index import build_corpus_index, index_status, search_corpus


def test_index_nonempty():
    build_corpus_index()
    st = index_status()
    assert st["chunk_count"] >= 8
    assert st["indexed"] is True


def test_search_hits():
    build_corpus_index()
    hits = search_corpus("артериальное давление измерение", top_k=2, min_score=0.04)
    assert len(hits) >= 1
