from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class ClubJoinRequest(Base):
    __tablename__ = "club_join_requests"

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

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    status = Column(
        String,
        default="pending",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    reviewed_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    club = relationship(
        "Club",
        back_populates="join_requests",
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
    )

    reviewed_by = relationship(
        "User",
        foreign_keys=[reviewed_by_user_id],
    )
