from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import analyze, dictionary, generate, help as help_route

app = FastAPI(title="NLP Dictionary Lab", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api", tags=["Анализ"])
app.include_router(dictionary.router, prefix="/api", tags=["Словарь"])
app.include_router(generate.router, prefix="/api", tags=["Генерация"])
app.include_router(help_route.router, prefix="/api", tags=["Справка"])

@app.get("/")
def root():
    return {"message": "API работает. Документация: /docs"}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "backend", "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)