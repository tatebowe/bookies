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


class ClubInvitation(Base):
    """A club asking a user to join.

    The mirror image of ClubJoinRequest, which is a user asking a club.
    """

    __tablename__ = "club_invitations"

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

    invited_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    invited_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    # pending | accepted | declined | revoked
    status = Column(
        String,
        default="pending",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    responded_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    club = relationship(
        "Club",
    )

    invited_user = relationship(
        "User",
        foreign_keys=[invited_user_id],
    )

    invited_by = relationship(
        "User",
        foreign_keys=[invited_by_user_id],
    )
