# src/backend/dependencies.py
from sqlalchemy.orm import Session, sessionmaker

from database.engine import engine

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=True)


def open_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
