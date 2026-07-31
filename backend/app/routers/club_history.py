from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.club_history import ClubHistoryResponse
from app.services.club_history_service import get_club_history
from app.services.permission_service import require_club_visibility

router = APIRouter(
    prefix="/clubs",
    tags=["Club History"],
)


@router.get(
    "/{club_id}/history",
    response_model=ClubHistoryResponse,
)
def club_history(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    require_club_visibility(
        db,
        club_id,
        current_user.id,
    )

    return get_club_history(
        db,
        club_id,
    )
