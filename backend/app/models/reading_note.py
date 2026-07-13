from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class ReadingNote(Base):
    __tablename__ = "reading_notes"

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

    club_reading_id = Column(
        Integer,
        ForeignKey("club_readings.id"),
        nullable=True,
    )

    reading_entry_id = Column(
        Integer,
        ForeignKey("reading_entries.id"),
        nullable=True,
    )

    title = Column(
        String,
        nullable=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="reading_notes",
    )

    club_reading = relationship(
        "ClubReading",
        back_populates="reading_notes",
    )

    reading_entry = relationship(
        "ReadingEntry",
        back_populates="reading_notes",
    )
