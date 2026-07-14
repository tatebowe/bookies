from datetime import datetime, timezone

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


def ensure_utc(value: datetime) -> datetime:
    """
    Ensure datetime comparisons are timezone aware.
    """

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc,
        )

    return value


def finalize_voting_cycle(
    db: Session,
    cycle: VotingCycle,
) -> VotingCycle:
    """
    Select the winning book and transition the cycle
    into reading phase.

    This happens automatically after voting closes.
    """

    if cycle.selected_book_id is not None:
        return cycle

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
            BookSuggestion.cycle_id == cycle.id,
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
        raise InvalidVotingCycleError(
            "No suggestions found",
        )

    highest_votes = results[0].vote_count

    winners = [result for result in results if result.vote_count == highest_votes]

    if len(winners) > 1:
        raise VotingTieError(
            "Voting resulted in a tie",
        )

    cycle.selected_book_id = winners[0].book_id
    cycle.phase = "reading"

    create_readings_for_cycle(
        db,
        cycle.club_id,
        cycle.id,
        cycle.selected_book_id,
    )

    return cycle


def update_cycle_phase(
    db: Session,
    cycle: VotingCycle,
) -> VotingCycle:
    """
    Automatically advance cycle state.
    """

    now = datetime.now(timezone.utc)

    voting_start = ensure_utc(
        cycle.voting_start_date,
    )

    voting_end = ensure_utc(
        cycle.voting_end_date,
    )

    discussion_date = ensure_utc(
        cycle.discussion_date,
    )

    old_phase = cycle.phase
    old_active = cycle.active

    if now < voting_start:
        cycle.phase = "suggestion"

    elif now < voting_end:
        cycle.phase = "voting"

    elif now < discussion_date:

        if cycle.selected_book_id is None:
            finalize_voting_cycle(
                db,
                cycle,
            )

        cycle.phase = "reading"

    else:
        cycle.phase = "completed"
        cycle.active = False

    if cycle.phase != old_phase or cycle.active != old_active:
        db.commit()
        db.refresh(cycle)

    return cycle


def get_active_cycle(
    db: Session,
    club_id: int,
) -> VotingCycle | None:
    """
    Return current active cycle and update phase.
    """

    cycle = (
        db.query(VotingCycle)
        .filter(
            VotingCycle.club_id == club_id,
            VotingCycle.active.is_(True),
        )
        .first()
    )

    if cycle is None:
        return None

    return update_cycle_phase(
        db,
        cycle,
    )


def create_voting_cycle(
    db: Session,
    club_id: int,
    suggestion_start_date: datetime,
    voting_start_date: datetime,
    voting_end_date: datetime,
    discussion_date: datetime,
    user_id: int,
    name: str | None = None,
) -> VotingCycle:
    """
    Create a voting cycle.

    Requires admin privileges.
    """

    require_club_admin(
        db,
        club_id,
        user_id,
    )

    if not (
        suggestion_start_date < voting_start_date < voting_end_date < discussion_date
    ):
        raise InvalidVotingCycleError(
            "Cycle dates must be in chronological order",
        )

    existing_cycle = get_active_cycle(
        db,
        club_id,
    )

    if existing_cycle:
        raise ActiveVotingCycleExistsError(
            "Club already has an active voting cycle",
        )

    cycle = VotingCycle(
        club_id=club_id,
        name=name,
        suggestion_start_date=suggestion_start_date,
        voting_start_date=voting_start_date,
        voting_end_date=voting_end_date,
        discussion_date=discussion_date,
        phase="suggestion",
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

    cycle = get_by_id(
        db,
        VotingCycle,
        cycle_id,
    )

    if cycle is None:
        raise VotingCycleNotFoundError(
            "Voting cycle not found",
        )

    return cycle


def close_voting_cycle(
    db: Session,
    cycle_id: int,
    user_id: int,
) -> VotingCycle:
    """
    Emergency manual close.
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
    cycle.phase = "completed"

    return save_and_refresh(
        db,
        cycle,
    )
