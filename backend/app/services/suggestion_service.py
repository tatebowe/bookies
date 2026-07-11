from sqlalchemy.orm import Session

from app.exceptions.suggestion_exceptions import (
    NotClubMemberError,
    SuggestionAlreadyExistsError,
    SuggestionNotFoundError,
)
from app.models.book import Book
from app.models.membership import ClubMembership
from app.models.suggestion import BookSuggestion
from app.services.helpers import get_by_id, save_and_refresh
from app.services.voting_cycle_service import get_active_cycle


def verify_club_membership(
    db: Session,
    club_id: int,
    user_id: int,
) -> bool:
    """
    Verify a user belongs to a club.
    """

    membership = (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
            ClubMembership.user_id == user_id,
        )
        .first()
    )

    return membership is not None


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

    if not verify_club_membership(
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
            BookSuggestion.book_id == book_id,
            BookSuggestion.cycle_id == cycle.id,
        )
        .first()
    )

    if existing:
        raise SuggestionAlreadyExistsError(
            "This book has already been suggested this cycle"
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
):
    """
    Get suggestions for the current voting cycle.
    """

    cycle = get_active_cycle(
        db,
        club_id,
    )

    if cycle is None:
        return []

    return (
        db.query(BookSuggestion)
        .filter(
            BookSuggestion.club_id == club_id,
            BookSuggestion.cycle_id == cycle.id,
        )
        .all()
    )


def get_suggestion_by_id(
    db: Session,
    suggestion_id: int,
):
    """
    Retrieve a suggestion.
    """

    suggestion = get_by_id(
        db,
        BookSuggestion,
        suggestion_id,
    )

    if suggestion is None:
        raise SuggestionNotFoundError("Suggestion not found")

    return suggestion
