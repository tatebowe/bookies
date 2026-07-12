from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions.club_reading_exceptions import (
    InvalidReadingStatusError,
)
from app.models.club_reading import ClubReading
from app.models.membership import ClubMembership
from app.services.helpers import get_by_id, save_and_refresh

VALID_STATUSES = {
    "not_started",
    "reading",
    "completed",
}


def create_readings_for_cycle(
    db: Session,
    club_id: int,
    cycle_id: int,
    book_id: int,
) -> list[ClubReading]:
    """
    Create a reading record for every club member.
    """

    members = (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
        )
        .all()
    )

    readings = []

    for member in members:
        reading = ClubReading(
            club_id=club_id,
            cycle_id=cycle_id,
            book_id=book_id,
            user_id=member.user_id,
            status="not_started",
        )

        db.add(reading)
        readings.append(reading)

    db.commit()

    for reading in readings:
        db.refresh(reading)

    return readings


def get_user_reading(
    db: Session,
    reading_id: int,
) -> ClubReading | None:
    """
    Retrieve a reading record.
    """

    return get_by_id(
        db,
        ClubReading,
        reading_id,
    )


def update_reading_status(
    db: Session,
    reading: ClubReading,
    status: str,
) -> ClubReading:
    """
    Update reading status.
    """

    if status not in VALID_STATUSES:
        raise InvalidReadingStatusError("Invalid reading status")

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
    reading: ClubReading,
    rating: float | None,
    review: str | None,
) -> ClubReading:

    if reading.status != "completed":
        raise InvalidReadingStatusError(
            "A review can only be added after completing the book"
        )

    reading.rating = rating
    reading.review = review

    return save_and_refresh(
        db,
        reading,
    )
