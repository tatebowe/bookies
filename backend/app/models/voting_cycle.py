from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class VotingCycle(Base):
    __tablename__ = "voting_cycles"

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

    name = Column(
        String,
        nullable=True,
    )

    suggestion_start_date = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    voting_start_date = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    voting_end_date = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    discussion_date = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    phase = Column(
        String,
        default="suggestion",
        nullable=False,
    )

    active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    selected_book_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    club = relationship(
        "Club",
        back_populates="voting_cycles",
    )

    suggestions = relationship(
        "BookSuggestion",
        back_populates="cycle",
        cascade="all, delete-orphan",
    )

    selected_book = relationship(
        "Book",
    )
