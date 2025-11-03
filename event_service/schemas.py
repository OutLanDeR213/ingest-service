from pydantic import BaseModel, ConfigDict, field_validator
from typing import Dict, Any
from datetime import datetime
import json


class EventCreate(BaseModel):
    """Модель для создания события (входные данные API)"""
    event_id: str
    occurred_at: datetime
    user_id: str
    event_type: str
    properties: Dict[str, Any] = {}


class EventResponse(BaseModel):
    """Модель для отображения события из БД (ответ API)"""
    event_id: str
    occurred_at: datetime
    user_id: str
    event_type: str
    properties: Dict[str, Any] = {}

    # ✅ позволяет создавать объект напрямую из SQLAlchemy модели
    model_config = ConfigDict(from_attributes=True)

    @field_validator("properties", mode="before")
    def ensure_dict(cls, v):
        """Если JSON хранится как строка, превращаем его в словарь"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v
