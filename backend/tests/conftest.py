"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base


@compiles(PGUUID, "sqlite")
def _compile_pg_uuid(element, compiler, **kw):
    """Render PostgreSQL UUID columns as CHAR when using SQLite in tests."""

    return "CHAR(36)"


@pytest.fixture
def db_session() -> Session:
    """Provide an isolated in-memory SQLite session for tests."""

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()
