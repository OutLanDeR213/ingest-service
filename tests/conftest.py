import pytest
from event_service.database import get_db
from event_service import models
from sqlalchemy.orm import Session
from datetime import datetime
import uuid


@pytest.fixture(scope="function")
def test_events():
    """Фикстура, создающая несколько тестовых событий перед аналитическими тестами"""
    db: Session = next(get_db())

    # Очистим таблицу перед тестом
    db.query(models.Event).delete()
    db.commit()

    test_data = [
        models.Event(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime(2025, 10, 30, 12, 0, 0),
            user_id="user1",
            event_type="login",
            properties={"device": "mobile"},
        ),
        models.Event(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime(2025, 10, 31, 14, 0, 0),
            user_id="user2",
            event_type="click",
            properties={"page": "home"},
        ),
        models.Event(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime(2025, 11, 1, 18, 0, 0),
            user_id="user1",
            event_type="purchase",
            properties={"price": 99},
        ),
    ]

    db.add_all(test_data)
    db.commit()

    yield

    # После теста — очистим таблицу
    db.query(models.Event).delete()
    db.commit()
    db.close()
