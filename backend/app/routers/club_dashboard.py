from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.club_dashboard import ClubDashboardResponse
from app.services.club_dashboard_service import get_club_dashboard

router = APIRouter(
    prefix="/clubs",
    tags=["Club Dashboard"],
)


@router.get(
    "/{club_id}/dashboard",
    response_model=ClubDashboardResponse,
)
def club_dashboard(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_club_dashboard(
        db,
        club_id,
        current_user.id,
    )
