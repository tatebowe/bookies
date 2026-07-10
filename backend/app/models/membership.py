from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class ClubMembership(Base):

    __tablename__ = "club_memberships"

    id = Column(
        Integer,
        primary_key=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    club_id = Column(
        Integer,
        ForeignKey("clubs.id"),
        nullable=False,
    )

    role = Column(
        String,
        default="member",
    )

    user = relationship(
        "User",
        back_populates="memberships",
    )

    club = relationship(
        "Club",
        back_populates="memberships",
    )
