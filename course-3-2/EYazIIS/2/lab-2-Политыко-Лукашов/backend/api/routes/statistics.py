from fastapi import APIRouter, Query
from core.dependencies import corpus

router = APIRouter(tags=["Статистика"])


@router.get("/stats/wordforms")
async def get_wordform_frequencies(
    doc_id: str | None = Query(None, description="ID документа (опционально)"),
    limit: int = Query(70, description="Количество слов в топе"),
    offset: int = Query(0, description="Смещение для пагинации")
):
    frequencies = corpus.get_wordform_frequencies(doc_id)
    
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    total = len(sorted_freq)
    paginated = sorted_freq[offset:offset + limit]
    
    return {
        "type": "wordforms",
        "total_unique": total,
        "total_tokens": sum(frequencies.values()),
        "limit": limit,
        "offset": offset,
        "frequencies": [{"word": w, "count": c} for w, c in paginated]
    }


@router.get("/stats/lemmas")
async def get_lemma_frequencies(
    doc_id: str | None = Query(None, description="ID документа (опционально)"),
    limit: int = Query(70, description="Количество лемм в топе"),
    offset: int = Query(0, description="Смещение для пагинации")
):
    frequencies = corpus.get_lemma_frequencies(doc_id)
    
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    total = len(sorted_freq)
    paginated = sorted_freq[offset:offset + limit]
    
    return {
        "type": "lemmas",
        "total_unique": total,
        "total_tokens": sum(frequencies.values()),
        "limit": limit,
        "offset": offset,
        "frequencies": [{"lemma": l, "count": c} for l, c in paginated]
    }


@router.get("/stats/pos")
async def get_pos_statistics(
    doc_id: str | None = Query(None, description="ID документа (опционально)")
):
    pos_stats = corpus.get_pos_statistics(doc_id)
    
    total = sum(pos_stats.values())
    percentages = {
        pos: round((count / total * 100), 2) if total > 0 else 0
        for pos, count in pos_stats.items()
    }
    
    return {
        "type": "parts_of_speech",
        "total": total,
        "statistics": [
            {"pos": pos, "count": count, "percentage": percentages[pos]}
            for pos, count in sorted(pos_stats.items(), key=lambda x: x[1], reverse=True)
        ]
    }


@router.get("/stats/grammars")
async def get_grammar_statistics(
    doc_id: str | None = Query(None, description="ID документа (опционально)")
):
    grammar_stats = corpus.get_grammar_statistics(doc_id)
    
    result: dict = {"type": "grammatical_categories"}
    
    for category, stats in grammar_stats.items():
        total = sum(stats.values())
        percentages = {
            val: round((count / total * 100), 2) if total > 0 else 0
            for val, count in stats.items()
        }
        result[category] = {
            "total": total,
            "values": [
                {"value": v, "count": c, "percentage": percentages[v]}
                for v, c in sorted(stats.items(), key=lambda x: x[1], reverse=True)
            ]
        }
    
    return result


@router.get("/stats/overview")
async def get_overview():
    docs = corpus.get_all_documents()
    total_docs = len(docs)
    total_words = sum(doc['word_count'] for doc in docs)
    
    wordform_freq = corpus.get_wordform_frequencies()
    lemma_freq = corpus.get_lemma_frequencies()
    pos_stats = corpus.get_pos_statistics()
    
    return {
        "total_documents": total_docs,
        "total_words": total_words,
        "unique_wordforms": len(wordform_freq),
        "unique_lemmas": len(lemma_freq),
        "parts_of_speech": len(pos_stats)
    }
