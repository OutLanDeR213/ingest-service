import pytest
from fastapi.testclient import TestClient
from datetime import date
from event_service.main import app

client = TestClient(app)


@pytest.mark.usefixtures("test_events")
def test_dau_stats():
    """Проверяет DAU — количество уникальных пользователей по дням."""
    response = client.get("/stats/dau?from_=2025-10-30&to=2025-11-02")
    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)
    assert all("date" in d and "unique_users" in d for d in data)

    total_users = sum(d["unique_users"] for d in data)
    assert total_users > 0


@pytest.mark.usefixtures("test_events")
def test_top_events():
    """Проверяет топ event_type по количеству."""
    response = client.get("/stats/top-events?from_=2025-10-30&to=2025-11-02&limit=5")
    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)
    assert all("event_type" in e and "count" in e for e in data)
    assert len(data) > 0


@pytest.mark.usefixtures("test_events")
def test_retention_stats():
    """Проверяет ретеншн (когортный анализ)."""
    response = client.get("/stats/retention?start_date=2025-10-30&windows=3")
    assert response.status_code == 200, response.text

    data = response.json()

    # backend возвращает список, а не словарь
    assert isinstance(data, list)
    assert all("day" in d and "retained_users" in d for d in data)
