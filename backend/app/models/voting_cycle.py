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

    start_date = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_date = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    active = Column(
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
        back_populates="voting_cycles",
    )
