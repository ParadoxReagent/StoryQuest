"""
SQLAlchemy database models for StoryQuest.
Phase 3: Core Story Engine Backend
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Session(Base):
    """Story session database model."""
    __tablename__ = "sessions"

    id = Column(
        PGUUID(as_uuid=True),
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

    # Relationship to story turns
    story_turns = relationship("StoryTurn", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id={self.id}, player={self.player_name}, theme={self.theme}, turns={self.turns})>"


class StoryTurn(Base):
    """Individual story turn database model."""
    __tablename__ = "story_turns"

    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    session_id = Column(
        PGUUID(as_uuid=True),
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

    # Relationship to session
    session = relationship("Session", back_populates="story_turns")

    def __repr__(self):
        return f"<StoryTurn(id={self.id}, session_id={self.session_id}, turn={self.turn_number})>"
