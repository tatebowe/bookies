from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.club_history import ClubHistoryResponse
from app.services.club_history_service import get_club_history

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
):

    return get_club_history(
        db,
        club_id,
    )
