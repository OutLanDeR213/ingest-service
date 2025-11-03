from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from . import models

def create_event(db: Session, event_data: dict):
    if db.query(models.Event).filter_by(event_id=event_data["event_id"]).first():
        return None
    event = models.Event(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def get_dau(db: Session, start: datetime, end: datetime):
    results = (
        db.query(
            func.date(models.Event.occurred_at).label("day"),
            func.count(func.distinct(models.Event.user_id)).label("unique_users")
        )
        .filter(models.Event.occurred_at >= start, models.Event.occurred_at <= end)
        .group_by(func.date(models.Event.occurred_at))
        .all()
    )
    return [{"date": str(r.day), "unique_users": r.unique_users} for r in results]

def get_top_events(db: Session, start: datetime, end: datetime, limit: int = 10):
    results = (
        db.query(models.Event.event_type, func.count().label("count"))
        .filter(models.Event.occurred_at >= start, models.Event.occurred_at <= end)
        .group_by(models.Event.event_type)
        .order_by(func.count().desc())
        .limit(limit)
        .all()
    )
    return [{"event_type": r.event_type, "count": r.count} for r in results]

def get_retention(db: Session, start_date: datetime, windows: int = 3):
    base_users = set(
        u[0] for u in db.query(models.Event.user_id)
        .filter(func.date(models.Event.occurred_at) == start_date.date())
        .distinct()
        .all()
    )
    if not base_users:
        return {"message": "Нет данных для базовой когорты", "start_date": str(start_date.date())}

    result = []
    for i in range(windows):
        day = start_date + timedelta(days=i)
        active = set(
            u[0] for u in db.query(models.Event.user_id)
            .filter(func.date(models.Event.occurred_at) == day.date())
            .distinct()
            .all()
        )
        retained = len(base_users & active)
        rate = round(retained / len(base_users), 3)
        result.append({"day": str(day.date()), "retained_users": retained, "retention_rate": rate})
    return result
