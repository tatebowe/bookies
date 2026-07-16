from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.club import Club
from app.models.membership import ClubMembership
from app.models.user import User
from app.schemas.club import (
    ClubCreate,
    ClubDiscoveryResponse,
    ClubMemberResponse,
    ClubMemberRoleUpdate,
    ClubResponse,
    ClubSettingsUpdate,
)
from app.services.club_service import (
    create_club,
    get_club_members,
    get_clubs_for_user,
    get_discoverable_clubs,
    search_public_clubs,
)
from app.services.helpers import save_and_refresh
from app.services.permission_service import require_club_owner

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


@router.patch("/{club_id}/settings", response_model=ClubResponse)
def update_settings(
    club_id: int,
    settings: ClubSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_club_owner(db, club_id, current_user.id)
    club = db.query(Club).filter(Club.id == club_id).first()
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")
    club.is_public = settings.is_public
    club.join_policy = settings.join_policy
    club.max_votes_per_user = settings.max_votes_per_user
    return save_and_refresh(db, club)


@router.patch("/{club_id}/members/{username}/role")
def update_member_role(
    club_id: int,
    username: str,
    update: ClubMemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_club_owner(db, club_id, current_user.id)
    membership = (
        db.query(ClubMembership)
        .join(User)
        .filter(ClubMembership.club_id == club_id, User.username == username)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=404, detail="Member not found")
    if membership.role == "owner":
        raise HTTPException(
            status_code=400, detail="The club owner role cannot be changed"
        )
    membership.role = update.role
    return {"message": "Member role updated", "role": membership.role}


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
