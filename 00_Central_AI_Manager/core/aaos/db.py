# -*- coding: utf-8 -*-
"""AAOS Database Connection and Session Management."""
import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import AAOSBase

# Unified AAOS database in the data folder
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
os.makedirs(DATA_DIR, exist_ok=True)
AAOS_DB_PATH = os.path.join(DATA_DIR, "aaos.db")
AAOS_DATABASE_URL = f"sqlite:///{AAOS_DB_PATH}"

engine = create_engine(
    AAOS_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


def init_db() -> None:
    """Initialize AAOS tables idempotently."""
    AAOSBase.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for AAOS database sessions."""
    init_db()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for AAOS database sessions."""
    init_db()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Aliases
init_aaos_db = init_db
get_aaos_db_session = get_session
