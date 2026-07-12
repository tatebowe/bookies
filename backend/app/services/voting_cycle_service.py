from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions.voting_cycle_exceptions import (
    ActiveVotingCycleExistsError,
    InvalidVotingCycleError,
    VotingCycleNotFoundError,
    VotingTieError,
)
from app.models.suggestion import BookSuggestion
from app.models.vote import BookVote
from app.models.voting_cycle import VotingCycle
from app.services.club_reading_service import create_readings_for_cycle
from app.services.helpers import get_by_id, save_and_refresh
from app.services.permission_service import require_club_admin


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
    user_id: int,
    name: str | None = None,
) -> VotingCycle:
    """
    Create a voting cycle for a club.

    Requires:
        User must be an admin or owner of the club.
    """

    require_club_admin(
        db,
        club_id,
        user_id,
    )

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
        phase="suggestion",
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
    Retrieve a voting cycle by ID.

    Raises:
        VotingCycleNotFoundError:
            If the cycle does not exist.
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
    user_id: int,
) -> VotingCycle:
    """
    Close a voting cycle.

    Requires:
        User must be an admin or owner of the club.
    """

    cycle = get_cycle_by_id(
        db,
        cycle_id,
    )

    require_club_admin(
        db,
        cycle.club_id,
        user_id,
    )

    cycle.active = False

    return save_and_refresh(
        db,
        cycle,
    )


def select_winner(
    db: Session,
    cycle_id: int,
    user_id: int,
) -> VotingCycle:
    """
    Select the winning book for a voting cycle.

    Raises:
        VotingTieError:
            If multiple books have the same highest vote count.
    """

    cycle = get_cycle_by_id(
        db,
        cycle_id,
    )

    require_club_admin(
        db,
        cycle.club_id,
        user_id,
    )

    if cycle.phase != "voting":
        raise InvalidVotingCycleError(
            "Winner can only be selected during the voting phase"
        )

    results = (
        db.query(
            BookSuggestion.book_id,
            func.count(BookVote.id).label("vote_count"),
        )
        .join(
            BookVote,
            BookVote.suggestion_id == BookSuggestion.id,
            isouter=True,
        )
        .filter(
            BookSuggestion.cycle_id == cycle_id,
        )
        .group_by(
            BookSuggestion.book_id,
        )
        .order_by(
            func.count(BookVote.id).desc(),
        )
        .all()
    )

    if not results:
        raise InvalidVotingCycleError("No suggestions found")

    highest_votes = results[0].vote_count

    winners = [result for result in results if result.vote_count == highest_votes]

    if len(winners) > 1:
        raise VotingTieError("Voting resulted in a tie")

    cycle.selected_book_id = winners[0].book_id
    cycle.phase = "reading"

    create_readings_for_cycle(
        db,
        cycle.club_id,
        cycle.id,
        cycle.selected_book_id,
    )

    return save_and_refresh(
        db,
        cycle,
    )


def open_voting_phase(
    db: Session,
    cycle_id: int,
    user_id: int,
) -> VotingCycle:

    cycle = get_cycle_by_id(
        db,
        cycle_id,
    )

    require_club_admin(
        db,
        cycle.club_id,
        user_id,
    )

    if cycle.phase != "suggestion":
        raise InvalidVotingCycleError("Cycle is not in suggestion phase")

    cycle.phase = "voting"

    return save_and_refresh(
        db,
        cycle,
    )
