from sqlalchemy.orm import Session

from app.exceptions.suggestion_exceptions import (
    NotClubMemberError,
    SuggestionAlreadyExistsError,
    SuggestionNotFoundError,
)
from app.models.book import Book
from app.models.suggestion import BookSuggestion
from app.services.club_service import is_club_member
from app.services.helpers import get_by_id, save_and_refresh
from app.services.voting_cycle_service import get_active_cycle


def create_suggestion(
    db: Session,
    club_id: int,
    book_id: int,
    user_id: int,
    anonymous: bool = True,
) -> BookSuggestion:
    """
    Create a book suggestion for an active voting cycle.
    """

    if not is_club_member(
        db,
        club_id,
        user_id,
    ):
        raise NotClubMemberError("User is not a member of this club")

    cycle = get_active_cycle(
        db,
        club_id,
    )

    if cycle is None:
        raise SuggestionNotFoundError("No active voting cycle exists")

    book = get_by_id(
        db,
        Book,
        book_id,
    )

    if book is None:
        raise SuggestionNotFoundError("Book not found")

    existing = (
        db.query(BookSuggestion)
        .filter(
            BookSuggestion.club_id == club_id,
            BookSuggestion.suggested_by_user_id == user_id,
            BookSuggestion.cycle_id == cycle.id,
        )
        .first()
    )

    if existing:
        raise SuggestionAlreadyExistsError(
            "User has already submitted a suggestion this cycle"
        )

    suggestion = BookSuggestion(
        club_id=club_id,
        book_id=book_id,
        suggested_by_user_id=user_id,
        cycle_id=cycle.id,
        anonymous=anonymous,
    )

    return save_and_refresh(
        db,
        suggestion,
    )


def get_club_suggestions(
    db: Session,
    club_id: int,
) -> list[BookSuggestion]:
    """
    Get suggestions for the current voting cycle.
    """

    cycle = get_active_cycle(
        db,
        club_id,
    )

    if cycle is None:
        return []

    suggestions = (
        db.query(BookSuggestion)
        .filter(
            BookSuggestion.club_id == club_id,
            BookSuggestion.cycle_id == cycle.id,
        )
        .all()
    )

    for suggestion in suggestions:
        suggestion.vote_count = len(suggestion.votes)

    return suggestions


def get_suggestion_by_id(
    db: Session,
    suggestion_id: int,
) -> BookSuggestion:
    """
    Retrieve a suggestion by ID.
    """

    suggestion = get_by_id(
        db,
        BookSuggestion,
        suggestion_id,
    )

    if suggestion is None:
        raise SuggestionNotFoundError("Suggestion not found")

    return suggestion
