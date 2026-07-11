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
from app.services.helpers import exists, get_by_id, save_and_refresh


def create_club(
    db: Session,
    club: ClubCreate,
    user: User,
) -> Club:
    """
    Create a new club and add the creator as owner.

    Raises:
        ClubAlreadyExistsError:
            If a club with the same name exists.
    """

    if exists(
        db,
        Club,
        name=club.name,
    ):
        raise ClubAlreadyExistsError("Club name already exists")

    new_club = Club(
        name=club.name,
        description=club.description,
    )

    new_club = save_and_refresh(
        db,
        new_club,
    )

    membership = ClubMembership(
        user_id=user.id,
        club_id=new_club.id,
        role="owner",
    )

    save_and_refresh(
        db,
        membership,
    )

    return new_club


def get_clubs_for_user(
    db: Session,
    user_id: int,
) -> list[Club]:
    """
    Return all clubs a user belongs to.
    """

    return (
        db.query(Club)
        .join(ClubMembership)
        .filter(
            ClubMembership.user_id == user_id,
        )
        .all()
    )


def add_member_to_club(
    db: Session,
    club_id: int,
    user_id: int,
) -> ClubMembership:
    """
    Add a user to a club.

    Raises:
        ClubNotFoundError:
            If the club does not exist.

        AlreadyMemberError:
            If the user is already a member.
    """

    get_club_by_id(
        db,
        club_id,
    )

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

    return save_and_refresh(
        db,
        membership,
    )


def get_club_members(
    db: Session,
    club_id: int,
) -> list[User]:
    """
    Return all users in a club.
    """

    get_club_by_id(
        db,
        club_id,
    )

    return (
        db.query(User)
        .join(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
        )
        .all()
    )


def is_club_member(
    db: Session,
    club_id: int,
    user_id: int,
) -> bool:
    """
    Check whether a user belongs to a club.
    """

    return (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
            ClubMembership.user_id == user_id,
        )
        .first()
        is not None
    )


def get_club_by_id(
    db: Session,
    club_id: int,
) -> Club:
    """
    Return a club by ID.

    Raises:
        ClubNotFoundError:
            If the club does not exist.
    """

    club = get_by_id(
        db,
        Club,
        club_id,
    )

    if club is None:
        raise ClubNotFoundError("Club not found")

    return club
