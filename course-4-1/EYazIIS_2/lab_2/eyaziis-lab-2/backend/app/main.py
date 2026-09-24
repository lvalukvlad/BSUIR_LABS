import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import bootstrap, evaluator, indexer
from .config import EXPORT_DIR
from .db import close_pool, init_pool
from .document_loader import UnsupportedFormatError, extract_text
from .indexer import save_recognition_result
from .language_model import recognize_language, summarize_recognition
from .migrate import run_migrations

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
    title="Система распознавания языка текста",
    description="Распознавание русского и немецкого языков по PDF-документам",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/recognize")
def api_recognize(file: UploadFile = File(...)) -> dict:
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="По варианту принимаются только PDF-документы")

    data = file.file.read()
    try:
        text = extract_text(filename, data)
    except UnsupportedFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="Не удалось извлечь текст из файла")

    runtime = bootstrap.get_runtime()
    if not runtime["profiles"]:
        raise HTTPException(status_code=503, detail="Профили языков недоступны. Выполните инициализацию.")

    results = recognize_language(text, runtime["profiles"], runtime["nn"])
    chosen = summarize_recognition(results)
    title = Path(file.filename or "документ").stem
    doc_id = indexer.save_document(
        title=title,
        body=text,
        source_file=file.filename,
        detected_language=chosen.get("language") or "unknown",
        result_json=results,
    )
    for method, payload in results.items():
        if not isinstance(payload, dict) or "method" not in payload:
            continue
        save_recognition_result(
            doc_id,
            method,
            payload.get("language") or "unknown",
            float(payload.get("confidence") or 0.0),
            payload,
        )

    return {
        "document_id": doc_id,
        "title": title,
        "text_length": len(text),
        "detected_language": chosen.get("language") or "unknown",
        "detected_languages": chosen.get("languages") or [],
        "shares": chosen.get("shares") or {},
        "confidence": chosen.get("confidence", 0.0),
        "method": chosen.get("method", "neural_network"),
        "results": results,
    }


@app.get("/api/documents")
def api_documents() -> dict:
    return {"documents": indexer.get_documents()}


@app.get("/api/documents/export")
def api_documents_export() -> JSONResponse:
    payload = {
        "documents": indexer.get_documents(),
        "stats": indexer.collection_stats(),
    }
    return JSONResponse(
        payload,
        headers={"Content-Disposition": "attachment; filename=recognition-results.json"},
    )


@app.get("/api/documents/{doc_id}")
def api_document(doc_id: int) -> dict:
    document = indexer.get_document(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return document


@app.delete("/api/documents/{doc_id}")
def api_delete_document(doc_id: int) -> dict:
    if not indexer.delete_document(doc_id):
        raise HTTPException(status_code=404, detail="Документ не найден")
    return {"message": "Документ удалён"}


@app.get("/api/stats")
def api_stats() -> dict:
    return indexer.collection_stats()


@app.get("/api/metrics")
def api_metrics(charts: bool = True) -> dict:
    evaluations = evaluator.compare_methods()
    payload = {
        "main": evaluations[evaluator.PRIMARY_MODEL],
        "comparison": [item["summary"] for item in evaluations.values()],
        "evaluations": evaluations,
    }
    if charts:
        payload["charts"] = evaluator.build_charts(evaluations)
    return payload


@app.post("/api/metrics/export")
def api_metrics_export() -> dict:
    evaluations = evaluator.compare_methods()
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
                "title": "Как работает система",
                "items": [
                    "Загрузите PDF-документ. Если в тексте есть и русский, и немецкий, система покажет оба языка.",
                    "Система распознаёт язык тремя методами: коротких слов, частотных слов и нейросетевым.",
                    "Язык считается найденным, если его доля не меньше 15%. Для каждого метода видны доли и расстояние OoP.",
                    "Эталонная тестовая коллекция загружается автоматически при первом запуске.",
                ],
            },
            {
                "title": "Методы распознавания",
                "items": [
                    "Коротких слов: ПОЯ из лексем длиной до 5 символов, встречавшихся более трёх раз.",
                    "Частотных слов: ПОЯ из 50 самых частотных лексем обучающего корпуса.",
                    "Нейросетевой: MLP на бинарных символьных N-граммах (N = 1..5).",
                    "Дополнительно считается расстояние OoP (Out-of-Place) между ранжированными профилями.",
                ],
            },
            {
                "title": "Оценка качества",
                "items": [
                    "Страница «Оценка» сравнивает методы по точности, полноте, F-мере и времени.",
                    "Графики можно выгрузить в каталог отчёта кнопкой «Выгрузить графики».",
                    "Список документов и результаты распознавания сохраняются в JSON и печатаются из браузера.",
                ],
            },
        ]
    }
