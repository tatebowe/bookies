from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.voting_cycle import (
    VotingCycleCreate,
    VotingCycleResponse,
)
from app.services.voting_cycle_service import (
    close_voting_cycle,
    create_voting_cycle,
    get_active_cycle,
    open_voting_phase,
    select_winner,
)

router = APIRouter(
    prefix="/clubs",
    tags=["Voting Cycles"],
)


@router.post(
    "/{club_id}/cycles",
    response_model=VotingCycleResponse,
)
def create_cycle(
    club_id: int,
    cycle: VotingCycleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_voting_cycle(
        db,
        club_id=club_id,
        suggestion_start_date=cycle.suggestion_start_date,
        voting_start_date=cycle.voting_start_date,
        voting_end_date=cycle.voting_end_date,
        discussion_date=cycle.discussion_date,
        name=cycle.name,
        user_id=user.id,
    )


@router.get(
    "/{club_id}/cycles/active",
    response_model=VotingCycleResponse | None,
)
def get_current_cycle(
    club_id: int,
    db: Session = Depends(get_db),
):
    return get_active_cycle(
        db,
        club_id,
    )


@router.post(
    "/cycles/{cycle_id}/close",
    response_model=VotingCycleResponse,
)
def close_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return close_voting_cycle(
        db,
        cycle_id,
        user.id,
    )


@router.post(
    "/cycles/{cycle_id}/winner",
    response_model=VotingCycleResponse,
)
def choose_winner(
    cycle_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return select_winner(
        db,
        cycle_id,
        user.id,
    )


@router.post(
    "/cycles/{cycle_id}/open-voting",
    response_model=VotingCycleResponse,
)
def open_voting(
    cycle_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return open_voting_phase(
        db,
        cycle_id,
        user.id,
    )
