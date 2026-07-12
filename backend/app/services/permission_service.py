from sqlalchemy.orm import Session

from app.exceptions.permission_exceptions import (
    NotClubAdminError,
    NotClubMemberError,
    NotClubOwnerError,
)
from app.models.membership import ClubMembership


def get_membership(
    db: Session,
    club_id: int,
    user_id: int,
) -> ClubMembership | None:

    return (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
            ClubMembership.user_id == user_id,
        )
        .first()
    )


def require_club_member(
    db: Session,
    club_id: int,
    user_id: int,
):
    membership = get_membership(
        db,
        club_id,
        user_id,
    )

    if membership is None:
        raise NotClubMemberError("User is not a member of this club")

    return membership


def require_club_admin(
    db: Session,
    club_id: int,
    user_id: int,
):

    membership = require_club_member(
        db,
        club_id,
        user_id,
    )

    if membership.role not in [
        "owner",
        "admin",
    ]:
        raise NotClubAdminError("User does not have admin permissions")

    return membership


def require_club_owner(
    db: Session,
    club_id: int,
    user_id: int,
):

    membership = require_club_member(
        db,
        club_id,
        user_id,
    )

    if membership.role != "owner":
        raise NotClubOwnerError("User is not the club owner")

    return membership
