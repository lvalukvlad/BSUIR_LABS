from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
from typing import Any
from core.dependencies import get_syntax_manager
from core.corpus.manager import SyntaxManager

router = APIRouter(tags=["Синтаксис"])


class UpdateDocumentRequest(BaseModel):
    content: str


class UpdateTokenRequest(BaseModel):
    sentence_id: int
    token_id: int
    syntax_role: str
    syntax_role_name: str


class TreeRequest(BaseModel):
    sentence_index: int | None = None


@router.get("/documents")
async def get_documents():
    manager = get_syntax_manager()
    return {
        "documents": manager.get_all_documents(),
        "total": len(manager.get_all_documents()),
    }


@router.post("/documents/load")
async def load_file(file: UploadFile = File(...), text_type: str = ""):
    manager = get_syntax_manager()

    allowed_extensions = {"txt", "rtf"}
    ext = file.filename.split(".")[-1].lower() if file.filename else "txt"

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат. Допустимы: {', '.join(allowed_extensions)}",
        )

    content = await file.read()

    doc = manager.load_file(content, file.filename or "unknown.txt")
    doc.text_type = text_type or "текст для синтаксического анализа"

    doc = manager.add_document(doc)

    return {
        "message": "Документ успешно загружен",
        "document": {
            "id": doc.id,
            "title": doc.title,
            "word_count": doc.word_count,
            "metadata": doc.to_dict()["metadata"],
        },
    }


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    manager = get_syntax_manager()
    doc = manager.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")

    return doc.to_dict()


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    manager = get_syntax_manager()
    if manager.delete_document(doc_id):
        return {"message": "Документ успешно удален"}
    raise HTTPException(status_code=404, detail="Документ не найден")


@router.put("/documents/{doc_id}")
async def update_document(doc_id: str, request: UpdateDocumentRequest):
    manager = get_syntax_manager()
    doc = manager.update_document(doc_id, request.content)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")

    analysis = manager.analyze_document(doc_id)

    updated_doc = manager.get_document(doc_id)
    analysis_time_ms = updated_doc.analysis_time_ms if updated_doc else 0

    return {
        "message": "Документ обновлен и переанализирован",
        "document": {"id": doc.id, "title": doc.title, "word_count": doc.word_count},
        "analysis": analysis,
        "statistics": manager.syntax_analyzer.get_statistics(analysis),
        "analysis_time_ms": analysis_time_ms,
    }


@router.post("/documents/{doc_id}/analyze")
async def analyze_document(doc_id: str):
    manager = get_syntax_manager()
    analysis = manager.analyze_document(doc_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Документ не найден")

    doc = manager.get_document(doc_id)
    analysis_time_ms = doc.analysis_time_ms if doc else 0

    return {
        "document_id": doc_id,
        "analysis": analysis,
        "statistics": manager.syntax_analyzer.get_statistics(analysis),
        "analysis_time_ms": analysis_time_ms,
    }


@router.get("/documents/{doc_id}/analysis")
async def get_document_analysis(doc_id: str):
    manager = get_syntax_manager()
    analysis = manager.get_analysis(doc_id)

    if analysis is None:
        raise HTTPException(status_code=404, detail="Документ не найден")

    doc = manager.get_document(doc_id)
    analysis_time_ms = doc.analysis_time_ms if doc else 0

    return {
        "document_id": doc_id,
        "analysis": analysis,
        "statistics": manager.syntax_analyzer.get_statistics(analysis),
        "analysis_time_ms": analysis_time_ms,
    }


@router.get("/documents/{doc_id}/relations")
async def get_document_relations(doc_id: str):
    manager = get_syntax_manager()
    relations = manager.get_relations(doc_id)

    if relations is None:
        raise HTTPException(status_code=404, detail="Документ не найден")

    return {"document_id": doc_id, "relations": relations}


@router.put("/documents/{doc_id}/token")
async def update_token(doc_id: str, request: UpdateTokenRequest):
    manager = get_syntax_manager()

    success = manager.update_token_role(
        doc_id,
        request.sentence_id,
        request.token_id,
        request.syntax_role,
        request.syntax_role_name,
    )

    if not success:
        raise HTTPException(status_code=404, detail="Документ или токен не найден")

    analysis = manager.get_analysis(doc_id)

    return {"message": "Токен обновлен", "analysis": analysis}


@router.get("/text/analyze")
async def analyze_text(text: str):
    import time

    manager = get_syntax_manager()

    doc = manager.load_file(text.encode("utf-8"), "temp.txt")
    doc = manager.add_document(doc)

    start_time = time.perf_counter()
    analysis = manager.analyze_document(doc.id)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    manager.delete_document(doc.id)

    return {
        "text": text,
        "analysis": analysis,
        "statistics": manager.syntax_analyzer.get_statistics(analysis),
        "analysis_time_ms": round(elapsed_ms, 2),
    }


@router.get("/documents/{doc_id}/dependency-tree")
async def get_dependency_tree(
    doc_id: str, sentence_index: int | None = Query(None, ge=1)
):
    manager = get_syntax_manager()
    result = manager.get_dependency_tree(doc_id, sentence_index)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/documents/{doc_id}/constituency-tree")
async def get_constituency_tree(
    doc_id: str, sentence_index: int | None = Query(None, ge=1)
):
    manager = get_syntax_manager()
    result = manager.get_constituency_tree(doc_id, sentence_index)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/text/analyze-trees")
async def analyze_text_trees(text: str = Query(..., min_length=1)):
    import time

    manager = get_syntax_manager()

    start_time = time.perf_counter()
    result = manager.analyze_text_trees(text)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    result["analysis_time_ms"] = round(elapsed_ms, 2)

    return result
