import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import dialog, help as help_route, sessions, stats
from core.corpus.index import build_corpus_index
from core.models import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    build_corpus_index()
    yield


init_db()

app = FastAPI(
    title="Естественно-языковая диалоговая система",
    description="Медицинская тематика, русский язык. Корпус, правила, контекст сессии.",
    version="6.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dialog.router, prefix="/api")
app.include_router(help_route.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Сервис работает",
        "docs": "/docs",
        "subject": "Медицина (русский)",
        "variant": 5,
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "nlp-dialog", "version": "6.1"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8010, reload=True)
