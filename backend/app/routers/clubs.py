from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.club import ClubCreate, ClubResponse
from app.services.club_service import (
    add_member_to_club,
    create_club,
    get_club_members,
    get_clubs_for_user,
)
from fastapi import APIRouter, Depends
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
    return create_club(
        db,
        club,
        current_user,
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


@router.post(
    "/{club_id}/join",
)
def join_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_member_to_club(
        db,
        club_id,
        current_user.id,
    )


@router.get(
    "/{club_id}/members",
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
