import csv
import sys
import json
import logging
from dateutil import parser
from typing import Dict, Any, List
from pydantic import BaseModel, ValidationError, field_validator
from .database import SessionLocal, engine
from . import models

# обычный запуск (sample)
#python -m event_service.import_events

# тестовая выборка
#python -m event_service.import_events data/events_100k.csv

# === Логирование ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("import_events")

error_log = open("import_errors.log", "w", encoding="utf-8")

# === Создаем таблицы, если их нет ===
models.Base.metadata.create_all(bind=engine)


# === Pydantic-модель для валидации событий ===
class EventSchema(BaseModel):
    event_id: str
    occurred_at: str
    user_id: str
    event_type: str
    properties_json: Any = {}

    @field_validator("occurred_at")
    def validate_date(cls, v):
        try:
            return parser.parse(v)
        except Exception:
            raise ValueError(f"Некорректный формат даты: {v}")

    @field_validator("properties_json", mode="before")
    def parse_json(cls, v):
        """Автоматически парсим JSON, даже если он строка"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v or {}


def import_events(path: str, batch_size: int = 1000):
    db = SessionLocal()
    imported, skipped, failed = 0, 0, 0
    batch: List[models.Event] = []

    try:
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_cols = {"event_id", "occurred_at", "user_id", "event_type"}
            if not required_cols.issubset(reader.fieldnames):
                logger.error(f"CSV должен содержать колонки: {required_cols}")
                sys.exit(1)

            for i, row in enumerate(reader, start=1):
                try:
                    # Проверка дубликатов
                    if db.query(models.Event).filter_by(event_id=row["event_id"]).first():
                        skipped += 1
                        continue

                    # Валидация через Pydantic
                    evt = EventSchema(**row)

                    # Создаем ORM объект
                    event = models.Event(
                        event_id=evt.event_id,
                        occurred_at=evt.occurred_at,
                        user_id=evt.user_id,
                        event_type=evt.event_type,
                        properties=evt.properties_json,  # ✅ теперь JSON уже распаршен
                    )

                    batch.append(event)
                    imported += 1

                    # Если достигли размера батча — сохраняем
                    if len(batch) >= batch_size:
                        db.bulk_save_objects(batch)
                        db.commit()
                        batch.clear()

                except ValidationError as ve:
                    failed += 1
                    msg = f"[{i}] Ошибка валидации: {ve}\nСтрока: {row}\n"
                    error_log.write(msg + "\n")
                except Exception as e:
                    failed += 1
                    msg = f"[{i}] Общая ошибка: {e}\nСтрока: {row}\n"
                    error_log.write(msg + "\n")

            # Сохраняем оставшиеся события
            if batch:
                db.bulk_save_objects(batch)
                db.commit()

        logger.info("✅ Импорт завершен успешно")
        logger.info(f"   ➕ Импортировано: {imported}")
        logger.info(f"   ⚙️ Пропущено (дубли): {skipped}")
        logger.info(f"   ❌ Ошибок: {failed}")

    except FileNotFoundError:
        logger.error(f"Файл не найден: {path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка при импорте: {e}")
        sys.exit(1)
    finally:
        db.close()
        error_log.close()


import os

if __name__ == "__main__":
    default_path = os.getenv("EVENTS_CSV_PATH", "data/events_sample.csv")
    path = sys.argv[1] if len(sys.argv) > 1 else default_path
    logger.info(f"📦 Импорт из файла: {path}")
    import_events(path)
