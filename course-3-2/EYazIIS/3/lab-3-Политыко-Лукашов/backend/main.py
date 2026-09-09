from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import syntax, help as help_route
from core.models import init_db

init_db()

app = FastAPI(
    title="Синтаксический анализатор",
    description="Система синтаксического анализа текста на русском языке",
    version="3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(syntax.router, prefix="/api", tags=["Синтаксис"])
app.include_router(help_route.router, prefix="/api", tags=["Справка"])


@app.get("/")
def root():
    return {
        "message": "Синтаксический анализатор работает",
        "docs": "/docs",
        "subject": "Синтаксический анализ русского текста"
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "syntax-analyzer", "version": "3.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
