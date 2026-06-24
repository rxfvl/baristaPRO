# db/database.py — SQLAlchemy engine and session factory

import os
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

# Store DB in user's home/.espressolab directory for persistence
APP_DIR = Path.home() / ".espressolab"
APP_DIR.mkdir(exist_ok=True)
DB_PATH = APP_DIR / "espressolab.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class get_session:
    """
    Context manager for SQLAlchemy sessions.
    Usage:
        with get_session() as db:
            db.query(...)
    """
    def __init__(self):
        self._session: Session = SessionLocal()

    def __enter__(self) -> Session:
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._session.rollback()
        self._session.close()
        return False  # Do not suppress exceptions


def init_db():
    """Create all tables if they don't exist."""
    from db import models  # noqa: F401 — ensures models are registered
    Base.metadata.create_all(bind=engine)
