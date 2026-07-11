from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions.voting_cycle_exceptions import (
    ActiveVotingCycleExistsError,
    InvalidVotingCycleError,
    VotingCycleNotFoundError,
)
from app.models.voting_cycle import VotingCycle
from app.services.helpers import get_by_id, save_and_refresh


def get_active_cycle(
    db: Session,
    club_id: int,
) -> VotingCycle | None:
    """
    Return the currently active voting cycle for a club.
    """

    return (
        db.query(VotingCycle)
        .filter(
            VotingCycle.club_id == club_id,
            VotingCycle.active.is_(True),
        )
        .first()
    )


def create_voting_cycle(
    db: Session,
    club_id: int,
    start_date: datetime,
    end_date: datetime,
    name: str | None = None,
) -> VotingCycle:
    """
    Create a voting cycle for a club.
    """

    if start_date >= end_date:
        raise InvalidVotingCycleError("Start date must be before end date")

    existing_cycle = get_active_cycle(
        db,
        club_id,
    )

    if existing_cycle:
        raise ActiveVotingCycleExistsError("Club already has an active voting cycle")

    cycle = VotingCycle(
        club_id=club_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        active=True,
    )

    return save_and_refresh(
        db,
        cycle,
    )


def get_cycle_by_id(
    db: Session,
    cycle_id: int,
) -> VotingCycle:
    """
    Retrieve a voting cycle.
    """

    cycle = get_by_id(
        db,
        VotingCycle,
        cycle_id,
    )

    if cycle is None:
        raise VotingCycleNotFoundError("Voting cycle not found")

    return cycle


def close_voting_cycle(
    db: Session,
    cycle_id: int,
) -> VotingCycle:
    """
    Close an active voting cycle.
    """

    cycle = get_cycle_by_id(
        db,
        cycle_id,
    )

    cycle.active = False

    return save_and_refresh(
        db,
        cycle,
    )
