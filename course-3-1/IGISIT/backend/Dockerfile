FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем дополнительные пакеты
RUN pip install --no-cache-dir \
    psycopg2-binary \
    sqlalchemy \
    pandas \
    scikit-learn \
    matplotlib

# Копируем остальной код
COPY . .

# Делаем init_db.sh исполняемым
RUN chmod +x init_db.sh 2>/dev/null || true

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

