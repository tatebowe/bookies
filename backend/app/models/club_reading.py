from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class ClubReading(Base):
    __tablename__ = "club_readings"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    club_id = Column(
        Integer,
        ForeignKey("clubs.id"),
        nullable=False,
    )

    cycle_id = Column(
        Integer,
        ForeignKey("voting_cycles.id"),
        nullable=False,
    )

    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    reading_entry_id = Column(
        Integer,
        ForeignKey("reading_entries.id"),
        nullable=False,
    )

    status = Column(
        String,
        default="not_started",
        nullable=False,
    )

    rating = Column(
        Float,
        nullable=True,
    )

    review = Column(
        Text,
        nullable=True,
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    finished_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    club = relationship(
        "Club",
    )

    cycle = relationship(
        "VotingCycle",
    )

    book = relationship(
        "Book",
    )

    user = relationship(
        "User",
    )

    discussion_notes = relationship(
        "DiscussionNote",
        back_populates="club_reading",
        cascade="all, delete-orphan",
    )

    reading_notes = relationship(
        "ReadingNote",
        back_populates="club_reading",
    )

    reading_entry = relationship(
        "ReadingEntry",
        back_populates="club_readings",
        foreign_keys=[reading_entry_id],
    )
