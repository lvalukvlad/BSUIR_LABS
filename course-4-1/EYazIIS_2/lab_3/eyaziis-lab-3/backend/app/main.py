import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager

from . import bootstrap, evaluator, indexer
from .config import EXPORT_DIR
from .db import close_pool, init_pool
from .document_loader import UnsupportedFormatError, extract_text, split_title
from .migrate import run_migrations
from .text_processing import detect_language

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DOMAINS = ("медицина", "критика изобразительного искусства")


@asynccontextmanager
async def lifespan(_app):
    init_pool()
    done = run_migrations()
    log.info("миграции: %s", len(done))
    stats = bootstrap.initialize()
    log.info("старт: %s", stats)
    yield
    close_pool()


app = FastAPI(title="Реферирование", version="0.3", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def flatten_kw(nodes, indent=0):
    lines = []
    for node in nodes:
        lines.append("  " * indent + node["term"])
        lines.extend(flatten_kw(node.get("children") or [], indent + 1))
    return lines


def export_text(doc):
    kws = flatten_kw(doc["keywords_json"])
    lines = [
        doc["title"],
        f"Язык: {doc['language']}",
        f"Область: {doc['domain']}",
        "",
        "Классический реферат",
        doc["summary_classic"],
        "",
        "Ключевые слова",
        *kws,
        "",
        "Базовый (первые 10)",
        doc.get("baseline_classic") or "",
        "",
        "Сеть",
    ]
    for arc in doc["network_json"] or []:
        lines.append(f"{arc['source']} — {arc['relation']} — {arc['target']}")
    return "\n".join(lines) + "\n"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/documents")
def api_documents():
    return {"documents": indexer.list_documents()}


@app.get("/api/documents/{doc_id}")
def api_document(doc_id: int):
    doc = indexer.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="нет такого документа")
    return doc


@app.get("/api/documents/{doc_id}/export")
def api_export(doc_id: int):
    doc = indexer.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="нет такого документа")
    name = f"referat-{doc_id}.txt"
    return PlainTextResponse(
        export_text(doc),
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@app.post("/api/documents/upload")
async def api_upload(file: UploadFile = File(...), domain: str = Form(...)):
    if domain not in DOMAINS:
        raise HTTPException(status_code=400, detail="выбери область из варианта")
    data = await file.read()
    try:
        raw = extract_text(file.filename or "document.txt", data)
    except UnsupportedFormatError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not raw.strip():
        raise HTTPException(status_code=400, detail="пустой файл")
    title, body = split_title(raw)
    lang = detect_language(body or raw)
    doc_id = indexer.add_document(
        title=title,
        body=body,
        language=lang,
        domain=domain,
        source_file=file.filename,
    )
    return {"document_id": doc_id, "title": title, "language": lang, "domain": domain}


@app.delete("/api/documents/{doc_id}")
def api_delete(doc_id: int):
    if not indexer.delete_document(doc_id):
        raise HTTPException(status_code=404, detail="нет такого документа")
    return {"message": "удалено"}


@app.get("/api/metrics")
def api_metrics(charts: bool = True):
    data = evaluator.evaluate()
    if charts:
        data["charts"] = evaluator.build_charts(data)
    return data


@app.post("/api/metrics/export")
def api_metrics_export():
    data = evaluator.evaluate()
    evaluator.build_charts(data, export_dir=EXPORT_DIR)
    return {"message": f"графики в {EXPORT_DIR}"}


@app.get("/api/help")
def api_help():
    return {
        "sections": [
            {
                "title": "Что считает программа",
                "items": [
                    "Классический реферат — 10 предложений с самым большим весом.",
                    "Рядом те же 10 первых предложений без весов, чтобы сравнить.",
                    "Дерево ключевых слов и словосочетаний.",
                    "Сеть: документ, область, понятия и связи между ними.",
                ],
            },
            {
                "title": "Вес предложения",
                "items": [
                    "Стопы, цифры и чужой алфавит выкидываем.",
                    "Posd = 1 − сколько символов до предложения / длина текста.",
                    "Posp то же самое, но внутри абзаца.",
                    "Score — сумма tf слова в предложении * его вес по коллекции.",
                    "Итог: Posd * Posp * Score.",
                ],
            },
            {
                "title": "Вариант 22",
                "items": [
                    "Русский и немецкий.",
                    "Медицина и критика изобразительного искусства.",
                    "Метод — sentence extraction.",
                ],
            },
        ]
    }
