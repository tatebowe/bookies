from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.exceptions.club_exceptions import (
    AlreadyMemberError,
    ClubAlreadyExistsError,
    ClubNotFoundError,
)
from app.models.user import User
from app.schemas.club import (
    ClubCreate,
    ClubMemberResponse,
    ClubResponse,
)
from app.services.club_service import (
    add_member_to_club,
    create_club,
    get_club_members,
    get_clubs_for_user,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/clubs",
    tags=["Clubs"],
)


@router.post(
    "/",
    response_model=ClubResponse,
)
def create_new_club(
    club: ClubCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_club(
            db,
            club,
            current_user,
        )
    except ClubAlreadyExistsError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[ClubResponse],
)
def get_my_clubs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_clubs_for_user(
        db,
        current_user.id,
    )


@router.post("/{club_id}/join")
def join_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return add_member_to_club(
            db,
            club_id,
            current_user.id,
        )

    except ClubNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except AlreadyMemberError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/{club_id}/members",
    response_model=list[ClubMemberResponse],
)
def get_members(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_club_members(
        db,
        club_id,
    )
