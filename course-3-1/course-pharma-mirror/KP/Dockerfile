# Используйте тот же образ Python
FROM python:3.11-slim

# Установите системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируйте requirements.txt и установите зависимости
COPY back/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Копируйте весь код из back
COPY back/. .

# Откройте порт
EXPOSE 8000

# Запустите FastAPI приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]