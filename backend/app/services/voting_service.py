from sqlalchemy.orm import Session

from app.exceptions.suggestion_exceptions import (
    NotClubMemberError,
)
from app.exceptions.vote_exceptions import (
    AlreadyVotedError,
    VoteLimitExceededError,
)
from app.models.vote import BookVote
from app.services.club_service import (
    get_club_by_id,
    is_club_member,
)
from app.services.helpers import save_and_refresh
from app.services.suggestion_service import (
    get_suggestion_by_id,
)


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

    if not is_club_member(
        db,
        suggestion.club_id,
        user_id,
    ):
        raise NotClubMemberError("User is not a member of this club")

    if has_user_voted(
        db,
        suggestion_id,
        user_id,
    ):
        raise AlreadyVotedError("User has already voted for this suggestion")

    club = get_club_by_id(
        db,
        suggestion.club_id,
    )

    current_votes = get_user_vote_count(
        db,
        suggestion.club_id,
        suggestion.cycle_id,
        user_id,
    )

    if current_votes >= club.max_votes_per_user:
        raise VoteLimitExceededError("Maximum votes reached")

    vote = BookVote(
        suggestion_id=suggestion.id,
        cycle_id=suggestion.cycle_id,
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
