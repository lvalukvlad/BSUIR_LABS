from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import corpus, search, statistics, help as help_route

app = FastAPI(
    title="Корпусный менеджер",
    description="Система управления кулинарным корпусом текстов",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(corpus.router, prefix="/api", tags=["Корпус"])
app.include_router(search.router, prefix="/api", tags=["Поиск"])
app.include_router(statistics.router, prefix="/api", tags=["Статистика"])
app.include_router(help_route.router, prefix="/api", tags=["Справка"])


@app.get("/")
def root():
    return {
        "message": "Корпусный менеджер работает",
        "docs": "/docs",
        "subject": "Кулинарные тексты"
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "corpus-manager", "version": "2.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
