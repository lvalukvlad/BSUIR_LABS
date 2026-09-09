from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from core.dependencies import corpus

router = APIRouter(tags=["Корпус"])


class UpdateDocumentRequest(BaseModel):
    content: str


class LoadDocumentRequest(BaseModel):
    author: str = ""
    date: str = ""
    genre: str = ""
    text_type: str = "кулинарный текст"


@router.get("/corpus")
async def get_documents():
    docs = corpus.get_all_documents()
    return {
        "documents": docs,
        "total": len(docs)
    }


@router.post("/corpus/load")
async def load_file(
    file: UploadFile = File(...),
    author: str = "",
    date: str = "",
    genre: str = "",
    text_type: str = "кулинарный текст"
):
    allowed_extensions = {'txt', 'rtf', 'pdf', 'doc', 'docx'}
    ext = file.filename.split('.')[-1].lower() if file.filename else 'txt'
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат. Допустимы: {', '.join(allowed_extensions)}"
        )
    
    content = await file.read()
    
    doc = corpus.load_file(content, file.filename or "unknown.txt")
    doc.author = author
    doc.date = date
    doc.genre = genre
    doc.text_type = text_type or "кулинарный текст"
    corpus.add_document(doc)
    
    return {
        "message": "Документ успешно загружен",
        "document": {
            "id": doc.id,
            "title": doc.title,
            "word_count": doc.word_count,
            "metadata": doc.to_dict()['metadata']
        }
    }


@router.get("/corpus/{doc_id}")
async def get_document(doc_id: str):
    doc = corpus.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    return doc.to_dict()


@router.delete("/corpus/{doc_id}")
async def delete_document(doc_id: str):
    if corpus.delete_document(doc_id):
        return {"message": "Документ успешно удален"}
    raise HTTPException(status_code=404, detail="Документ не найден")


@router.put("/corpus/{doc_id}")
async def update_document(doc_id: str, request: UpdateDocumentRequest):
    doc = corpus.update_document(doc_id, request.content)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return doc.to_dict()


@router.get("/corpus/{doc_id}/analyzed")
async def get_analyzed_document(doc_id: str):
    doc = corpus.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    analysis = corpus.analyze_document(doc_id)
    
    return {
        "document_id": doc_id,
        "title": doc.title,
        "total_tokens": len(analysis),
        "analysis": analysis
    }


@router.get("/corpus/{doc_id}/lemmas")
async def get_document_lemmas(doc_id: str):
    doc = corpus.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    lemmas = corpus.get_lemmas(doc_id)
    
    sorted_lemmas = sorted(lemmas.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "document_id": doc_id,
        "total_unique_lemmas": len(lemmas),
        "lemmas": [{"lemma": l, "count": c} for l, c in sorted_lemmas]
    }


@router.get("/corpus/{doc_id}/metadata")
async def get_document_metadata(doc_id: str):
    doc = corpus.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    return doc.to_dict()['metadata']
