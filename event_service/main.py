import os
import logging
import json
from typing import List
from dateutil.parser import parse
from fastapi import FastAPI, Request, Depends, HTTPException, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base, get_db
from . import models, schemas, crud, import_events

# -------------------------
# Логирование
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("event_service")

# -------------------------
# Lifespan: стартовый импорт CSV и создание таблиц
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # -----------------
    # Создаём таблицы в выбранной базе
    # -----------------
    logger.info("⚙️ Создание таблиц в базе...")
    Base.metadata.create_all(bind=engine)

    # -----------------
    # Выбор CSV
    # -----------------
    mode = "test" if os.getenv("TEST_MODE", "0").strip() == "1" else "sample"
    csv_file = f"events_{mode}.csv"
    csv_path = os.path.join(os.getcwd(), "data", csv_file)

    logger.info(f"TEST_MODE={os.getenv('TEST_MODE')}, using CSV: {csv_path}")

    if os.path.exists(csv_path):
        logger.info(f"📥 Импортируем CSV: {csv_path}")
        import_events.import_events(csv_path)
    else:
        logger.warning(f"⚠️ CSV файл не найден: {csv_path}")

    yield  # приложение работает здесь

# -------------------------
# Создание FastAPI
# -------------------------
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Event Analytics Dashboard", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda request, exc: JSONResponse(status_code=429, content={"detail": "Too many requests"})
)
app.add_middleware(SlowAPIMiddleware)

# -------------------------
# Пути к шаблонам и статике
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # event_service
templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

if not os.path.exists(templates_dir):
    logger.warning(f"⚠️ Папка шаблонов не найдена: {templates_dir}")
if not os.path.exists(static_dir):
    logger.warning(f"⚠️ Папка статики не найдена: {static_dir}")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# -------------------------
# Prometheus метрики
# -------------------------
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# -------------------------
# Маршруты
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/events/view", response_class=HTMLResponse)
@limiter.limit("60/minute")
def view_events(request: Request, db: Session = Depends(get_db)):
    events = db.query(models.Event).order_by(models.Event.occurred_at.desc()).all()
    events_data = [
        {
            "event_id": e.event_id,
            "user_id": e.user_id,
            "event_type": e.event_type,
            "event_date": e.occurred_at.strftime("%Y-%m-%d %H:%M:%S") if e.occurred_at else "-",
            "properties_json": json.dumps(e.properties or {}, ensure_ascii=False, indent=2)
        }
        for e in events
    ]
    return templates.TemplateResponse("events.html", {"request": request, "events": events_data})

@app.get("/events")
@limiter.limit("60/minute")
def get_events(request: Request, db: Session = Depends(get_db)):
    events = db.query(models.Event).order_by(models.Event.occurred_at.desc()).all()
    return [
        {
            "event_id": e.event_id,
            "user_id": e.user_id,
            "event_type": e.event_type,
            "occurred_at": e.occurred_at.strftime("%Y-%m-%d %H:%M:%S") if e.occurred_at else None,
            "properties": e.properties or {}
        }
        for e in events
    ]

@app.post("/events")
@limiter.limit("100/minute")
def ingest_events(request: Request, events: List[schemas.EventCreate] = Body(...), db: Session = Depends(get_db)):
    created = []
    for e in events:
        existing = db.query(models.Event).filter_by(event_id=e.event_id).first()
        if existing:
            created.append(existing)
            continue
        evt = models.Event(**e.model_dump())
        db.add(evt)
        db.commit()
        db.refresh(evt)
        created.append(evt)
    return created

@app.get("/stats/dau")
@limiter.limit("60/minute")
def stats_dau(request: Request, from_: str = Query(...), to: str = Query(...), db: Session = Depends(get_db)):
    try:
        start, end = parse(from_), parse(to)
    except Exception:
        raise HTTPException(status_code=400, detail="Неправильный формат даты")
    return JSONResponse(content=crud.get_dau(db, start, end))

@app.get("/stats/top-events")
@limiter.limit("60/minute")
def stats_top_events(request: Request, from_: str = Query(...), to: str = Query(...), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        start, end = parse(from_), parse(to)
    except Exception:
        raise HTTPException(status_code=400, detail="Неправильный формат даты")
    return JSONResponse(content=crud.get_top_events(db, start, end, limit))

@app.get("/stats/retention")
@limiter.limit("60/minute")
def stats_retention(request: Request, start_date: str = Query(...), windows: int = Query(3), db: Session = Depends(get_db)):
    try:
        start = parse(start_date)
    except Exception:
        raise HTTPException(status_code=400, detail="Неправильный формат даты")
    return JSONResponse(content=crud.get_retention(db, start, windows))
