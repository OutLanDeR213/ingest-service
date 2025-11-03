import pytest
from fastapi.testclient import TestClient
from event_service.main import app, get_db
from event_service import models
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

client = TestClient(app)


@pytest.fixture()
def db_session():
    """
    Безопасно берём сессию из get_db() и гарантированно закрываем генератор.
    Это корректнее, чем просто next(get_db()) без закрытия.
    """
    gen = get_db()
    session = next(gen)
    try:
        # очистим таблицу перед тестом — чтобы тесты были изолированы
        session.query(models.Event).delete()
        session.commit()
        yield session
    finally:
        try:
            gen.close()  # это вызовет finally в get_db() и закроет сессию
        except Exception:
            # на всякий случай, если генератор уже закрыт
            session.close()


def test_post_and_get_events(db_session: Session):
    """Проверяем успешную отправку и получение событий"""
    event_data = [
        {
            "event_id": str(uuid.uuid4()),
            "occurred_at": "2025-10-30T12:00:00Z",
            "user_id": "user123",
            "event_type": "login",
            "properties": {"device": "mobile"},
        }
    ]

    # POST /events
    response = client.post("/events", json=event_data)
    assert response.status_code == 200, f"POST /events failed: {response.text}"
    data = response.json()
    assert len(data) == 1, f"unexpected response length: {data}"
    assert data[0]["event_type"] == "login"

    # GET /events
    response = client.get("/events")
    assert response.status_code == 200, f"GET /events failed: {response.text}"
    events = response.json()
    assert any(e["user_id"] == "user123" for e in events), "posted event not found in GET /events"


def test_idempotency_post_events(db_session: Session):
    """Проверяем, что дубликаты по event_id не создаются"""
    eid = str(uuid.uuid4())
    event = {
        "event_id": eid,
        "occurred_at": "2025-10-31T08:00:00Z",
        "user_id": "userX",
        "event_type": "click",
        "properties": {"page": "home"},
    }

    # Отправляем 2 раза подряд
    r1 = client.post("/events", json=[event])
    r2 = client.post("/events", json=[event])

    assert r1.status_code == 200, f"first POST failed: {r1.text}"
    assert r2.status_code == 200, f"second POST failed: {r2.text}"

    # Проверяем, что в БД только 1 запись
    all_events = db_session.query(models.Event).filter(models.Event.event_id == eid).all()
    assert len(all_events) == 1, f"expected 1 event, got {len(all_events)}"
