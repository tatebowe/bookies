from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.profile import ProfileResponse
from app.services.profile_service import get_profile_by_username

router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"],
)


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
