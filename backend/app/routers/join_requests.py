from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.join_request import JoinRequestResponse
from app.services.join_request_service import (
    approve_join_request,
    get_pending_requests,
    reject_join_request,
    request_to_join,
)

router = APIRouter(
    prefix="/clubs",
    tags=["Join Requests"],
)


@router.post(
    "/{club_id}/join",
)
def join_club(
    club_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Request to join a club.

    Open clubs immediately add the user.
    Request clubs create a pending request.
    """

    result = request_to_join(
        db,
        club_id,
        user.id,
    )

    if hasattr(result, "status"):
        return {
            "message": "Join request submitted",
            "status": result.status,
        }

    return {
        "message": "Successfully joined club",
    }


@router.get(
    "/{club_id}/join-requests",
    response_model=list[JoinRequestResponse],
)
def list_join_requests(
    club_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    List pending join requests for club admins.
    """

    return get_pending_requests(
        db,
        club_id,
        user.id,
    )


@router.post(
    "/join-requests/{request_id}/approve",
    response_model=JoinRequestResponse,
)
def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Approve a join request.
    """

    return approve_join_request(
        db,
        request_id,
        user.id,
    )


@router.post(
    "/join-requests/{request_id}/reject",
    response_model=JoinRequestResponse,
)
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Reject a join request.
    """

    return reject_join_request(
        db,
        request_id,
        user.id,
    )
