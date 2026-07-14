from sqlalchemy.orm import Session

from app.exceptions.cycle_phase_exceptions import InvalidCyclePhaseError
from app.exceptions.vote_exceptions import (
    AlreadyVotedError,
    VoteLimitExceededError,
)
from app.models.vote import BookVote
from app.services.club_service import get_club_by_id
from app.services.helpers import save_and_refresh
from app.services.permission_service import require_club_member
from app.services.suggestion_service import get_suggestion_by_id
from app.services.voting_cycle_service import get_active_cycle


def get_user_vote_count(
    db: Session,
    club_id: int,
    cycle_id: int,
    user_id: int,
) -> int:
    """
    Return the number of votes a user has cast
    during the current voting cycle.
    """

    return (
        db.query(BookVote)
        .filter(
            BookVote.user_id == user_id,
            BookVote.cycle_id == cycle_id,
        )
        .count()
    )


def has_user_voted(
    db: Session,
    suggestion_id: int,
    user_id: int,
) -> bool:
    """
    Return True if the user has already voted
    for this suggestion.
    """

    return (
        db.query(BookVote)
        .filter(
            BookVote.suggestion_id == suggestion_id,
            BookVote.user_id == user_id,
        )
        .first()
        is not None
    )


def cast_vote(
    db: Session,
    suggestion_id: int,
    user_id: int,
) -> BookVote:
    """
    Cast a vote for a suggestion.
    """

    suggestion = get_suggestion_by_id(
        db,
        suggestion_id,
    )

    cycle = get_active_cycle(
        db,
        suggestion.club_id,
    )

    if cycle is None or cycle.phase != "voting":
        raise InvalidCyclePhaseError(
            "Voting is not currently open",
        )

    require_club_member(
        db,
        suggestion.club_id,
        user_id,
    )

    if has_user_voted(
        db,
        suggestion_id,
        user_id,
    ):
        raise AlreadyVotedError(
            "User has already voted for this suggestion",
        )

    club = get_club_by_id(
        db,
        suggestion.club_id,
    )

    current_votes = get_user_vote_count(
        db,
        suggestion.club_id,
        cycle.id,
        user_id,
    )

    if current_votes >= club.max_votes_per_user:
        raise VoteLimitExceededError(
            "Maximum votes reached",
        )

    vote = BookVote(
        suggestion_id=suggestion.id,
        cycle_id=cycle.id,
        user_id=user_id,
    )

    return save_and_refresh(
        db,
        vote,
    )


def get_vote_count(
    db: Session,
    suggestion_id: int,
) -> int:
    """
    Return total votes for a suggestion.
    """

    return (
        db.query(BookVote)
        .filter(
            BookVote.suggestion_id == suggestion_id,
        )
        .count()
    )


def remove_vote(
    db: Session,
    suggestion_id: int,
    user_id: int,
) -> None:
    """
    Remove a user's vote from a suggestion.
    """

    vote = (
        db.query(BookVote)
        .filter(
            BookVote.suggestion_id == suggestion_id,
            BookVote.user_id == user_id,
        )
        .first()
    )

    if vote is None:
        raise AlreadyVotedError(
            "Vote does not exist",
        )

    db.delete(vote)
    db.commit()
