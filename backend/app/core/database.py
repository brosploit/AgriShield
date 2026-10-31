"""AgriShield AI - Database Engine & Session Management

Configures SQLAlchemy 2.0 engine, declarative base, and FastAPI session dependency.
Supports PostgreSQL (production/development) and SQLite (testing).
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Engine configuration
raw_db_url = settings.DATABASE_URL
# Normalize Render/Heroku legacy 'postgres://' to SQLAlchemy 2.0 compatible 'postgresql+psycopg2://'
if raw_db_url.startswith("postgres://"):
    db_url = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif raw_db_url.startswith("postgresql://") and not raw_db_url.startswith("postgresql+"):
    db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    db_url = raw_db_url

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        db_url,
        connect_args=connect_args,
    )
else:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        connect_args={"client_encoding": "utf8"},
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 ORM models."""
    pass


def get_db() -> Generator:
    """FastAPI dependency for yielding database session with transaction safety."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

