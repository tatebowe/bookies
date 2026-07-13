from datetime import datetime

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

from app.database.database import Base


class ReadingEntry(Base):
    __tablename__ = "reading_entries"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="not_started",
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
        DateTime,
        nullable=True,
    )

    finished_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="reading_entries",
    )

    book = relationship(
        "Book",
    )

    reading_notes = relationship(
        "ReadingNote",
        back_populates="reading_entry",
    )

    club_readings = relationship(
        "ClubReading",
        back_populates="reading_entry",
    )
