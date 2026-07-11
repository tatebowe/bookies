from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.voting_cycle import (
    VotingCycleCreate,
    VotingCycleResponse,
)
from app.services.voting_cycle_service import (
    close_voting_cycle,
    create_voting_cycle,
    get_active_cycle,
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
):
    return create_voting_cycle(
        db,
        club_id=club_id,
        start_date=cycle.start_date,
        end_date=cycle.end_date,
        name=cycle.name,
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
):
    return close_voting_cycle(
        db,
        cycle_id,
    )


@router.post(
    "/cycles/{cycle_id}/winner",
    response_model=VotingCycleResponse,
)
def choose_winner(
    cycle_id: int,
    db: Session = Depends(get_db),
):
    return select_winner(
        db,
        cycle_id,
    )
