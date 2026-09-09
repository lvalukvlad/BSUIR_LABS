import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import bootstrap, evaluator, indexer, search_service
from .config import DEFAULT_TOP_K, EXPORT_DIR, PRF_ENABLED_BY_DEFAULT
from .db import close_pool, init_pool
from .document_loader import UnsupportedFormatError, extract_text
from .migrate import run_migrations
from .query_assistant import highlight_document, suggest
from .text_processing import normalize

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_pool()
    applied = run_migrations()
    log.info("Применено миграций: %s", len(applied))
    stats = bootstrap.initialize()
    log.info("Инициализация: %s", stats)
    yield
    close_pool()


app = FastAPI(
    title="Информационно-поисковая система",
    description="Вероятностная модель поиска (Okapi BM25) по русскоязычной коллекции",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=50)
    model: str = Field(default="bm25")
    use_prf: bool = PRF_ENABLED_BY_DEFAULT
    date_from: str | None = None
    date_to: str | None = None


class DocumentRequest(BaseModel):
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/search")
def api_search(request: SearchRequest) -> dict:
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Пустой поисковый запрос")
    return search_service.search(
        query=request.query,
        top_k=request.top_k,
        use_prf=request.use_prf,
        model=request.model,
        date_from=request.date_from,
        date_to=request.date_to,
    )


@app.get("/api/suggest")
def api_suggest(prefix: str = "") -> dict:
    return {"prefix": prefix, "suggestions": suggest(prefix)}


@app.get("/api/documents")
def api_documents() -> dict:
    return {"documents": indexer.list_documents()}


@app.get("/api/documents/{doc_id}")
def api_document(doc_id: int, query: str = "") -> dict:
    document = indexer.get_document(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    document["highlighted"] = highlight_document(document["body"], set(normalize(query)))
    document["key_terms"] = indexer.top_terms(doc_id)
    return document


@app.post("/api/documents")
def api_add_document(request: DocumentRequest) -> dict:
    doc_id = indexer.index_document(title=request.title, body=request.text)
    return {"document_id": doc_id, "message": "Документ добавлен и проиндексирован"}


@app.post("/api/documents/upload")
async def api_upload(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    try:
        text = extract_text(file.filename or "", data)
    except UnsupportedFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="Не удалось извлечь текст из файла")

    title = Path(file.filename or "документ").stem
    doc_id = indexer.index_document(title=title, body=text, source_file=file.filename)
    return {
        "document_id": doc_id,
        "title": title,
        "characters": len(text),
        "message": "Файл загружен и проиндексирован",
    }


@app.delete("/api/documents/{doc_id}")
def api_delete_document(doc_id: int) -> dict:
    if not indexer.delete_document(doc_id):
        raise HTTPException(status_code=404, detail="Документ не найден")
    return {"message": "Документ удалён из индекса"}


@app.get("/api/stats")
def api_stats() -> dict:
    return indexer.collection_stats()


@app.get("/api/metrics")
def api_metrics(top_k: int = DEFAULT_TOP_K, charts: bool = True) -> dict:
    evaluations = evaluator.compare_models(top_k=top_k)
    payload = {
        "main": evaluations[evaluator.PRIMARY_MODEL],
        "comparison": [item["summary"] for item in evaluations.values()],
    }
    if charts:
        payload["charts"] = evaluator.build_charts(evaluations)
    return payload


@app.post("/api/metrics/export")
def api_metrics_export(top_k: int = DEFAULT_TOP_K) -> dict:
    evaluations = evaluator.compare_models(top_k=top_k)
    evaluator.build_charts(evaluations, export_dir=EXPORT_DIR)
    return {"message": f"Графики сохранены в {EXPORT_DIR}"}


@app.post("/api/init-db")
def api_init_db(force: bool = False) -> dict:
    return bootstrap.initialize(force=force)


@app.get("/api/help")
def api_help() -> dict:
    return {
        "sections": [
            {
                "title": "Как искать",
                "items": [
                    "Введите запрос обычными словами: система сама приведёт их к начальной форме.",
                    "Порядок слов не важен, регистр не учитывается.",
                    "Опечатки исправляются автоматически, исходный запрос показывается рядом.",
                    "По мере ввода появляются подсказки из словаря коллекции.",
                ],
            },
            {
                "title": "Как читать выдачу",
                "items": [
                    "Документы отсортированы по убыванию оценки релевантности RSV.",
                    "В сниппете подсвечены слова запроса, найденные в документе.",
                    "Под сниппетом перечислены совпавшие слова и их словоформы.",
                    "Заголовок документа является ссылкой на его полный текст.",
                ],
            },
            {
                "title": "Модель поиска",
                "items": [
                    "Ранжирование выполняется вероятностной моделью Okapi BM25.",
                    "Веса терминов вычисляются по формуле Робертсона -- Спарк Джонс.",
                    "Флажок «Обратная связь» включает второй проход поиска с пересчётом "
                    "весов по псевдорелевантному множеству.",
                    "Для сравнения доступна базовая векторная модель TF-IDF.",
                ],
            },
            {
                "title": "Оценка качества",
                "items": [
                    "На странице оценки рассчитываются точность, полнота, F-меры, P@k, MAP и nDCG.",
                    "Строится 11-точечная кривая полноты-точности.",
                    "Результаты трёх моделей ранжирования сравниваются на одном графике.",
                ],
            },
        ]
    }
