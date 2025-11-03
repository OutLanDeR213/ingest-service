# Event Ingest & Analytics Service

Сервис для збору подій (events) та базової аналітики (DAU, топ-события, retention).

Реалізовано на **FastAPI + SQLAlchemy (SQLite) + Docker + Prometheus/Grafana**.

---

## 📂 Структура проєкту

- `event_service/` — код FastAPI сервісу, модулі: `main.py`, `database.py`, `crud.py`, `models.py`, `import_events.py`, `benchmark_import.py`, `schemas.py`
- `event_db_data/` - папки з росположенням сгенерованих файлі БД
- `prometheus` - папка з скріптом прометеус
- `tests/` — unit та інтеграційні тести через `pytest`
- `data/` — CSV-файли для інгесту (`events_sample.csv`, `events_test.csv`)
- `docker-compose.yml` — підняття сервісів та тестів
- `LEARNED.md` — досвід інтеграції FastAPI + SQLite + Docker
- `ADR.md` — архітектурне рішення та вибір інструментів
- `README.md` - файл з описанням як користвуватися проєктом
- `requirements.txt` - файл з залежностями
---

## 🛠️ Попередні вимоги

- Docker (>= 20.x)
- Docker Compose (>= 2.x)
- Python 3.17 (для локального запуску без Docker)

---

## 🚀 Запуск сервісу через Docker
docker compose build -d ingest_events_app
docker compose up -d ingest_events_app

docker compose build -d ingest_events_test
docker compose up -d ingest_events_test

docker compose run --rm tests

docker compose up prometheus grafana -d

docker compose down