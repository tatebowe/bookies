from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.club import (
    ClubCreate,
    ClubDiscoveryResponse,
    ClubMemberResponse,
    ClubResponse,
)
from app.services.club_service import (
    create_club,
    get_club_members,
    get_clubs_for_user,
    get_discoverable_clubs,
    search_public_clubs,
)

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


@router.get(
    "/discover",
    response_model=list[ClubDiscoveryResponse],
)
def discover_clubs(
    db: Session = Depends(get_db),
):
    return get_discoverable_clubs(
        db,
    )


@router.get(
    "/search",
    response_model=list[ClubDiscoveryResponse],
)
def search_clubs(
    q: str,
    db: Session = Depends(get_db),
):
    return search_public_clubs(
        db,
        q,
    )
