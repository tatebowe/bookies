from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class BookSuggestion(Base):
    __tablename__ = "book_suggestions"

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

    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=False,
    )

    suggested_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    anonymous = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    club = relationship(
        "Club",
        back_populates="suggestions",
    )

    book = relationship(
        "Book",
    )

    suggested_by = relationship(
        "User",
    )

    votes = relationship(
        "BookVote",
        back_populates="suggestion",
    )

    cycle_id = Column(
        Integer,
        ForeignKey("voting_cycles.id"),
        nullable=False,
    )

    cycle = relationship(
        "VotingCycle",
        back_populates="suggestions",
    )
