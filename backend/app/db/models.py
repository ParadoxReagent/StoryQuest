"""
SQLAlchemy database models for StoryQuest.
Phase 3: Core Story Engine Backend
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type when available, otherwise uses
    CHAR(36) for SQLite and other databases, storing as stringified hex values.
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid4.__class__):
                return str(value)
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid4.__class__):
                from uuid import UUID
                return UUID(value)
            else:
                return value


class Session(Base):
    """Story session database model."""
    __tablename__ = "sessions"

    id = Column(
        GUID,
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    player_name = Column(String(100), nullable=False)
    age_range = Column(String(10), nullable=False)
    theme = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    turns = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Performance indexes for common query patterns
    __table_args__ = (
        Index('idx_session_active_created', 'is_active', 'created_at'),
        Index('idx_session_last_activity', 'last_activity'),
    )

    # Relationship to story turns
    story_turns = relationship("StoryTurn", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id={self.id}, player={self.player_name}, theme={self.theme}, turns={self.turns})>"


class StoryTurn(Base):
    """Individual story turn database model."""
    __tablename__ = "story_turns"

    id = Column(
        GUID,
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    session_id = Column(
        GUID,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    turn_number = Column(Integer, nullable=False, index=True)
    scene_text = Column(Text, nullable=False)
    scene_id = Column(String(100), nullable=False)
    player_choice = Column(Text, nullable=True)
    custom_input = Column(Text, nullable=True)
    story_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Performance: Composite index for common query pattern (get turns by session, ordered)
    __table_args__ = (
        Index('idx_turn_session_number', 'session_id', 'turn_number'),
        Index('idx_turn_session_created', 'session_id', 'created_at'),
    )

    # Relationship to session
    session = relationship("Session", back_populates="story_turns")

    def __repr__(self):
        return f"<StoryTurn(id={self.id}, session_id={self.session_id}, turn={self.turn_number})>"
