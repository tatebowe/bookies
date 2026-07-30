from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.exceptions.moderation_exceptions import NameNotAllowedError
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile_service import (
    get_profile_by_username,
    get_profile_settings,
    update_profile_settings,
)

router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"],
)


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return get_profile_settings(db, current_user)


@router.patch("/me", response_model=ProfileResponse)
def update_my_profile(
    update: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_profile_settings(
            db,
            current_user,
            update.display_name,
            update.club_updates,
            update.cycle_reminders,
            update.reading_activity,
        )
    except NameNotAllowedError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/{username}",
    response_model=ProfileResponse,
)
def get_profile(
    username: str,
    db: Session = Depends(get_db),
):
    return get_profile_by_username(
        db,
        username,
    )
