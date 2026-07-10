from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class BookVote(Base):
    __tablename__ = "book_votes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    suggestion_id = Column(
        Integer,
        ForeignKey("book_suggestions.id"),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    suggestion = relationship(
        "BookSuggestion",
        back_populates="votes",
    )

    user = relationship(
        "User",
    )

    __table_args__ = (
        UniqueConstraint(
            "suggestion_id",
            "user_id",
            name="unique_user_suggestion_vote",
        ),
    )

    cycle_id = Column(
        Integer,
        ForeignKey("voting_cycles.id"),
        nullable=False,
    )
