from sqlalchemy import Column, String, DateTime, JSON
from .database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True)
    occurred_at = Column(DateTime, index=True)
    user_id = Column(String, index=True)
    event_type = Column(String, index=True)
    properties = Column(JSON, default=dict)
