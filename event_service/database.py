import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(BASE_DIR, "event_db_data")
os.makedirs(DB_FOLDER, exist_ok=True)

MAIN_DB_PATH = os.path.join(DB_FOLDER, "event_db.sqlite3")
TEST_DB_PATH = os.path.join(DB_FOLDER, "event_db_test.sqlite3")

def get_database_url():
    """Выбираем базу в зависимости от режима тестирования"""
    if os.getenv("TEST_MODE") == "1":
        print("⚙️ Используется ТЕСТОВАЯ база данных:", TEST_DB_PATH)
        return f"sqlite:///{TEST_DB_PATH}"
    print("💾 Используется ОСНОВНАЯ база данных:", MAIN_DB_PATH)
    return f"sqlite:///{MAIN_DB_PATH}"

SQLALCHEMY_DATABASE_URL = get_database_url()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
