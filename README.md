# Event Ingest & Analytics Service

Сервис для збору подій (events) та базової аналітики (DAU, топ-события, retention).

Реалізовано на **FastAPI + SQLAlchemy (SQLite) + Docker + Prometheus/Grafana**.

---

## 📂 Структура проєкту

- `event_service/` — код FastAPI сервісу, модулі: `main.py`, `database.py`, `crud.py`, `models.py`, `import_events.py`, `benchmark_import.py`, `schemas.py`
- `tests/` — unit та інтеграційні тести через `pytest`
- `data/` — CSV-файли для інгесту (`events_sample.csv`, `events_test.csv`)
- `docker-compose.yml` — підняття сервісів та тестів
- `LEARNED.md` — досвід інтеграції FastAPI + SQLite + Docker
- `ADR.md` — архітектурне рішення та вибір інструментів

---

## 🛠️ Попередні вимоги

- Docker (>= 20.x)
- Docker Compose (>= 2.x)
- Python 3.13 (для локального запуску без Docker)

---

## 🚀 Запуск сервісу через Docker

### 1. Підняти всі сервіси (робочий + тестовий + метрики)

```bash
docker compose up --build