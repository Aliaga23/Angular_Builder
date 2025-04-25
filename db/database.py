from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

DATABASE_URL = "postgresql://postgres:ofqUdVWPrcracqBEpVLkHLWaqriakDOU@tramway.proxy.rlwy.net:28353/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ⬇️ ESTA es la función que faltaba
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
