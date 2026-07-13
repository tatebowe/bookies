from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions.club_history_exceptions import (
    ClubHistoryNotFoundError,
)
from app.models.book import Book
from app.models.club import Club
from app.models.club_reading import ClubReading
from app.models.voting_cycle import VotingCycle


def get_club_history(
    db: Session,
    club_id: int,
):

    club = (
        db.query(Club)
        .filter(
            Club.id == club_id,
        )
        .first()
    )

    if club is None:
        raise ClubHistoryNotFoundError("Club not found")

    cycles = (
        db.query(VotingCycle)
        .filter(
            VotingCycle.club_id == club_id,
            VotingCycle.selected_book_id.isnot(None),
        )
        .order_by(VotingCycle.end_date.desc())
        .all()
    )

    history = []

    for cycle in cycles:

        book = db.query(Book).filter(Book.id == cycle.selected_book_id).first()

        progress = (
            db.query(
                ClubReading.status,
                func.count(ClubReading.id),
            )
            .filter(
                ClubReading.cycle_id == cycle.id,
            )
            .group_by(
                ClubReading.status,
            )
            .all()
        )

        started = sum(count for status, count in progress if status != "not_started")

        completed = sum(count for status, count in progress if status == "completed")

        history.append(
            {
                "cycle_id": cycle.id,
                "book": book,
                "start_date": cycle.start_date,
                "end_date": cycle.end_date,
                "members_started": started,
                "members_completed": completed,
            }
        )

    return {
        "club_id": club.id,
        "club_name": club.name,
        "history": history,
    }
