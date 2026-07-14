from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    username = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    display_name = Column(
        String,
        nullable=True,
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash = Column(
        String,
        nullable=True,
    )

    google_id = Column(
        String,
        unique=True,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    memberships = relationship(
        "ClubMembership",
        back_populates="user",
    )

    join_requests = relationship(
        "ClubJoinRequest",
        foreign_keys="ClubJoinRequest.user_id",
        back_populates="user",
    )

    reading_entries = relationship(
        "ReadingEntry",
        back_populates="user",
    )

    reading_notes = relationship(
        "ReadingNote",
        back_populates="user",
    )
