"""
Database connection and session management.
Phase 3: Core Story Engine Backend
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import DatabaseConfig
from app.db.models import Base

logger = logging.getLogger(__name__)


class Database:
    """Database manager for StoryQuest."""

    def __init__(self, config: DatabaseConfig):
        """
        Initialize database with configuration.

        Args:
            config: Database configuration
        """
        self.config = config
        self.engine = None
        self.session_factory = None
        self.is_async = False

        # Determine if we're using async or sync engine
        if config.url.startswith("sqlite"):
            # SQLite uses synchronous engine
            self.is_async = False
            self.engine = create_engine(
                config.url,
                echo=config.echo,
                connect_args={"check_same_thread": False}  # Required for SQLite
            )
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
        else:
            # PostgreSQL uses async engine
            self.is_async = True
            async_url = config.url.replace("postgresql://", "postgresql+asyncpg://")
            self.engine = create_async_engine(
                async_url,
                echo=config.echo
            )
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )

    def create_tables(self):
        """Create all database tables."""
        if self.is_async:
            raise RuntimeError("Cannot use create_tables() with async engine. Use init_db() instead.")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    async def init_db(self):
        """Initialize database (async version)."""
        if not self.is_async:
            # For sync engines, just create tables directly
            self.create_tables()
            return

        # For async engines
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully (async)")

    def get_session(self) -> Session:
        """
        Get a database session (synchronous).

        Returns:
            SQLAlchemy Session instance

        Raises:
            RuntimeError: If using async engine
        """
        if self.is_async:
            raise RuntimeError("Cannot use get_session() with async engine. Use get_async_session() instead.")
        return self.session_factory()

    async def get_async_session(self) -> AsyncSession:
        """
        Get an async database session.

        Returns:
            SQLAlchemy AsyncSession instance

        Raises:
            RuntimeError: If using sync engine
        """
        if not self.is_async:
            raise RuntimeError("Cannot use get_async_session() with sync engine. Use get_session() instead.")
        return self.session_factory()

    @asynccontextmanager
    async def session_scope(self) -> AsyncGenerator[Session, None]:
        """
        Provide a transactional scope for database operations.

        Yields:
            Database session

        Example:
            async with db.session_scope() as session:
                session.add(my_object)
                # Session will be committed automatically
        """
        if self.is_async:
            session = self.session_factory()
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
        else:
            session = self.session_factory()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    async def close(self):
        """Close database connections."""
        if self.engine:
            if self.is_async:
                await self.engine.dispose()
            else:
                self.engine.dispose()
            logger.info("Database connections closed")


# Global database instance
_database: Database = None


def init_database(config: DatabaseConfig) -> Database:
    """
    Initialize the global database instance.

    Args:
        config: Database configuration

    Returns:
        Database instance
    """
    global _database
    _database = Database(config)
    return _database


def get_database() -> Database:
    """
    Get the global database instance.

    Returns:
        Database instance

    Raises:
        RuntimeError: If database not initialized
    """
    if _database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _database


# Dependency for FastAPI
def get_db_session():
    """
    FastAPI dependency for getting database session.

    Yields:
        Database session
    """
    db = get_database()
    if db.is_async:
        raise RuntimeError("Use get_async_db_session() for async databases")

    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def get_async_db_session():
    """
    FastAPI dependency for getting async database session.

    Yields:
        Async database session
    """
    db = get_database()
    if not db.is_async:
        raise RuntimeError("Use get_db_session() for sync databases")

    async with db.session_scope() as session:
        yield session
