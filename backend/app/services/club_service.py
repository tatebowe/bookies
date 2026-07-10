from sqlalchemy.orm import Session

from app.exceptions.club_exceptions import (
    AlreadyMemberError,
    ClubAlreadyExistsError,
    ClubNotFoundError,
)
from app.models.club import Club
from app.models.membership import ClubMembership
from app.models.user import User
from app.schemas.club import ClubCreate


def create_club(
    db: Session,
    club: ClubCreate,
    user: User,
) -> Club:
    """
    Create a new club and add the creator as owner.
    """

    new_club = Club(
        name=club.name,
        description=club.description,
    )

    existing = db.query(Club).filter(Club.name == club.name).first()

    if existing:
        raise ClubAlreadyExistsError("Club name already exists")

    db.add(new_club)
    db.commit()
    db.refresh(new_club)

    membership = ClubMembership(
        user_id=user.id,
        club_id=new_club.id,
        role="owner",
    )

    db.add(membership)
    db.commit()

    return new_club


def get_clubs_for_user(
    db: Session,
    user_id: int,
):
    """
    Return all clubs a user belongs to.
    """

    return (
        db.query(Club)
        .join(ClubMembership)
        .filter(ClubMembership.user_id == user_id)
        .all()
    )


def add_member_to_club(
    db: Session,
    club_id: int,
    user_id: int,
):
    club = get_club_by_id(
        db,
        club_id,
    )

    if club is None:
        raise ClubNotFoundError("Club not found")

    existing_member = (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
            ClubMembership.user_id == user_id,
        )
        .first()
    )

    if existing_member:
        raise AlreadyMemberError("User is already a member of this club")

    membership = ClubMembership(
        club_id=club_id,
        user_id=user_id,
        role="member",
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return membership


def get_club_members(
    db: Session,
    club_id: int,
):
    """
    Return all users in a club.
    """

    return (
        db.query(User)
        .join(ClubMembership)
        .filter(ClubMembership.club_id == club_id)
        .all()
    )


def get_club_by_id(
    db: Session,
    club_id: int,
) -> Club:

    club = db.get(
        Club,
        club_id,
    )

    if club is None:
        raise ClubNotFoundError("Club not found")

    return club
