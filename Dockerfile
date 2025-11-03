FROM python:3.13-slim

# === Базовые настройки ===
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# === Устанавливаем зависимости ОС ===
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# === Устанавливаем Python-зависимости ===
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# === Копируем код приложения ===
COPY . .

# === Настраиваем entrypoint ===
RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# === Открываем порт ===
EXPOSE 8000

# === Переменные окружения ===
ENV IMPORT_ON_START=true

# === Команда запуска ===
CMD ["uvicorn", "event_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
