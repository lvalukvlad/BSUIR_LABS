import uvicorn
from config.settings import get_settings

def main():
    settings = get_settings()

    print("=" * 50)
    print("🚀 Медицинский AI Ассистент")
    print("=" * 50)
    print(f"📡 API: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"🤖 Модель: {settings.OLLAMA_MODEL}")
    print(f"📊 Логирование: {settings.LOG_LEVEL}")
    print("=" * 50)

    uvicorn.run(
        "api.fastapi_app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=True
    )

if __name__ == "__main__":
    main()