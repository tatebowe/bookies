from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class DiscussionNote(Base):
    __tablename__ = "discussion_notes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    club_reading_id = Column(
        Integer,
        ForeignKey("club_readings.id"),
        nullable=False,
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

    club_reading = relationship(
        "ClubReading",
        back_populates="discussion_notes",
    )
