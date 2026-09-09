FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Копирование всего кода
COPY . .

EXPOSE 8000

# Запуск FastAPI приложения
CMD ["uvicorn", "api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
