from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.exceptions.join_request_exceptions import (
    InvalidJoinRequestError,
    JoinRequestAlreadyExistsError,
    JoinRequestNotFoundError,
)
from app.models.join_request import ClubJoinRequest
from app.models.membership import ClubMembership
from app.services.club_reading_service import create_reading_for_member
from app.services.club_service import get_club_by_id
from app.services.helpers import get_by_id, save_and_refresh
from app.services.permission_service import require_club_admin
from app.services.voting_cycle_service import get_active_cycle


def add_current_reading_if_available(
    db: Session,
    club_id: int,
    user_id: int,
) -> None:
    """
    If the club currently has an active reading cycle,
    create a reading record for the new member.
    """

    cycle = get_active_cycle(
        db,
        club_id,
    )

    if cycle and cycle.phase == "reading" and cycle.selected_book_id:
        create_reading_for_member(
            db,
            club_id,
            cycle.id,
            cycle.selected_book_id,
            user_id,
        )


def request_to_join(
    db: Session,
    club_id: int,
    user_id: int,
) -> ClubJoinRequest | ClubMembership:
    """
    Request to join a club.

    Behavior depends on club join policy:

    open:
        Immediately creates membership.

    request:
        Creates a pending join request.

    invite:
        Rejects the request.
    """

    club = get_club_by_id(
        db,
        club_id,
    )

    existing_membership = (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
            ClubMembership.user_id == user_id,
        )
        .first()
    )

    if existing_membership:
        raise JoinRequestAlreadyExistsError("User is already a member of this club")

    if club.join_policy == "open":
        membership = ClubMembership(
            club_id=club_id,
            user_id=user_id,
            role="member",
        )

        save_and_refresh(
            db,
            membership,
        )

        add_current_reading_if_available(
            db,
            club_id,
            user_id,
        )

        return membership

    if club.join_policy == "invite":
        raise InvalidJoinRequestError("This club requires an invitation to join")

    existing_request = (
        db.query(ClubJoinRequest)
        .filter(
            ClubJoinRequest.club_id == club_id,
            ClubJoinRequest.user_id == user_id,
            ClubJoinRequest.status == "pending",
        )
        .first()
    )

    if existing_request:
        raise JoinRequestAlreadyExistsError("Join request already exists")

    join_request = ClubJoinRequest(
        club_id=club_id,
        user_id=user_id,
        status="pending",
    )

    return save_and_refresh(
        db,
        join_request,
    )


def get_join_request_by_id(
    db: Session,
    request_id: int,
) -> ClubJoinRequest:
    """
    Retrieve a join request.
    """

    request = get_by_id(
        db,
        ClubJoinRequest,
        request_id,
    )

    if request is None:
        raise JoinRequestNotFoundError("Join request not found")

    return request


def get_pending_requests(
    db: Session,
    club_id: int,
    user_id: int,
) -> list[ClubJoinRequest]:
    """
    Return pending join requests for admins.
    """

    require_club_admin(
        db,
        club_id,
        user_id,
    )

    return (
        db.query(ClubJoinRequest)
        .filter(
            ClubJoinRequest.club_id == club_id,
            ClubJoinRequest.status == "pending",
        )
        .all()
    )


def approve_join_request(
    db: Session,
    request_id: int,
    user_id: int,
) -> ClubJoinRequest:
    """
    Approve a join request.
    """

    join_request = get_join_request_by_id(
        db,
        request_id,
    )

    require_club_admin(
        db,
        join_request.club_id,
        user_id,
    )

    if join_request.status != "pending":
        raise InvalidJoinRequestError("Join request has already been processed")

    membership = ClubMembership(
        club_id=join_request.club_id,
        user_id=join_request.user_id,
        role="member",
    )

    save_and_refresh(
        db,
        membership,
    )

    add_current_reading_if_available(
        db,
        join_request.club_id,
        join_request.user_id,
    )

    join_request.status = "approved"
    join_request.reviewed_at = datetime.now(timezone.utc)
    join_request.reviewed_by_user_id = user_id

    return save_and_refresh(
        db,
        join_request,
    )


def reject_join_request(
    db: Session,
    request_id: int,
    user_id: int,
) -> ClubJoinRequest:
    """
    Reject a join request.
    """

    join_request = get_join_request_by_id(
        db,
        request_id,
    )

    require_club_admin(
        db,
        join_request.club_id,
        user_id,
    )

    if join_request.status != "pending":
        raise InvalidJoinRequestError("Join request has already been processed")

    join_request.status = "rejected"
    join_request.reviewed_at = datetime.now(timezone.utc)
    join_request.reviewed_by_user_id = user_id

    return save_and_refresh(
        db,
        join_request,
    )
