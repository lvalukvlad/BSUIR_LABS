from fastapi import APIRouter, Query
from core.dependencies import corpus

router = APIRouter(tags=["Поиск"])


@router.get("/search")
async def search_text(
    q: str = Query(..., description="Поисковый запрос"),
    doc_id: str | None = Query(None, description="ID документа (опционально)")
):
    if not q:
        return {"results": [], "total": 0}
    
    results = corpus.search(q, doc_id)
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }


@router.get("/concordance")
async def get_concordance(
    q: str = Query(..., description="Слово для конкорданса"),
    doc_id: str | None = Query(None, description="ID документа (опционально)"),
    context: int = Query(5, description="Количество слов слева/справа")
):
    if not q:
        return {"concordance": [], "total": 0}
    
    results = corpus.concordance(q, doc_id, context)
    
    return {
        "query": q,
        "context_words": context,
        "concordance": results,
        "total": len(results)
    }


@router.get("/concordance/kwic")
async def get_kwic(
    q: str = Query(..., description="Слово для KWIC"),
    doc_id: str | None = Query(None, description="ID документа (опционально)")
):
    if not q:
        return {"kwic": [], "total": 0}
    
    results = corpus.concordance(q, doc_id, 5)
    
    kwic = []
    for item in results:
        kwic.append({
            "document_id": item["document_id"],
            "document_title": item["document_title"],
            "left": item["left"],
            "keyword": item["keyword"],
            "right": item["right"],
        })
    
    return {
        "query": q,
        "kwic": kwic,
        "total": len(kwic)
    }
