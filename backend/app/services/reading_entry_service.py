from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions.reading_entry_exceptions import (
    InvalidReadingEntryStatusError,
    ReadingEntryNotFoundError,
    UnauthorizedReadingEntryError,
)
from app.models.reading_entry import ReadingEntry
from app.services.helpers import get_by_id, save_and_refresh

VALID_STATUSES = {
    "not_started",
    "reading",
    "completed",
}


def create_reading_entry(
    db: Session,
    user_id: int,
    book_id: int,
) -> ReadingEntry:
    """
    Add a book to a user's personal library.
    """

    reading = ReadingEntry(
        user_id=user_id,
        book_id=book_id,
        status="not_started",
    )

    return save_and_refresh(
        db,
        reading,
    )


def get_user_reading_entries(
    db: Session,
    user_id: int,
) -> list[ReadingEntry]:
    """
    Get all personal reading entries for a user.
    """

    return (
        db.query(ReadingEntry)
        .filter(
            ReadingEntry.user_id == user_id,
        )
        .all()
    )


def get_reading_entry(
    db: Session,
    reading_entry_id: int,
    user_id: int,
) -> ReadingEntry:
    """
    Retrieve a user's personal reading entry.
    """

    reading = get_by_id(
        db,
        ReadingEntry,
        reading_entry_id,
    )

    if reading is None:
        raise ReadingEntryNotFoundError("Reading entry not found")

    if reading.user_id != user_id:
        raise UnauthorizedReadingEntryError(
            "User is not authorized to access this reading entry"
        )

    return reading


def update_reading_status(
    db: Session,
    reading: ReadingEntry,
    status: str,
) -> ReadingEntry:
    """
    Update personal reading status.
    """

    if status not in VALID_STATUSES:
        raise InvalidReadingEntryStatusError("Invalid reading status")

    reading.status = status

    if status == "reading" and reading.started_at is None:
        reading.started_at = datetime.utcnow()

    if status == "completed" and reading.finished_at is None:
        reading.finished_at = datetime.utcnow()

    return save_and_refresh(
        db,
        reading,
    )


def update_reading_review(
    db: Session,
    reading: ReadingEntry,
    rating: float | None,
    review: str | None,
) -> ReadingEntry:
    """
    Add rating and review after completion.
    """

    if reading.status != "completed":
        raise InvalidReadingEntryStatusError(
            "A review can only be added after completing the book"
        )

    reading.rating = rating
    reading.review = review

    return save_and_refresh(
        db,
        reading,
    )
