from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Club(Base):

    __tablename__ = "clubs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    description = Column(
        String,
        nullable=True,
    )

    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    memberships = relationship(
        "ClubMembership",
        back_populates="club",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    suggestions = relationship(
        "BookSuggestion",
        back_populates="club",
    )

    max_votes_per_user = Column(
        Integer,
        default=1,
        nullable=False,
    )

    voting_cycles = relationship(
        "VotingCycle",
        back_populates="club",
    )

    tie_break_method = Column(
        String,
        default="runoff",
        nullable=False,
    )

    join_policy = Column(
        String,
        default="request",
        nullable=False,
    )

    join_requests = relationship(
        "ClubJoinRequest",
        back_populates="club",
    )
