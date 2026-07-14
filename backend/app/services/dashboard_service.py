from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.club_reading import ClubReading
from app.models.membership import ClubMembership
from app.models.voting_cycle import VotingCycle


def get_user_dashboard(
    db: Session,
    user_id: int,
):
    """
    Return dashboard information for a user.
    """

    memberships = (
        db.query(ClubMembership)
        .filter(
            ClubMembership.user_id == user_id,
        )
        .all()
    )

    clubs = []

    for membership in memberships:

        club = membership.club

        active_cycle = (
            db.query(VotingCycle)
            .filter(
                VotingCycle.club_id == club.id,
                VotingCycle.active.is_(True),
            )
            .first()
        )

        current_book = None

        if active_cycle and active_cycle.selected_book_id:
            current_book = (
                db.query(Book)
                .filter(
                    Book.id == active_cycle.selected_book_id,
                )
                .first()
            )

        current_reading = None

        if active_cycle:
            current_reading = (
                db.query(ClubReading)
                .filter(
                    ClubReading.user_id == user_id,
                    ClubReading.cycle_id == active_cycle.id,
                )
                .first()
            )

        clubs.append(
            {
                "club": club,
                "active_cycle": active_cycle,
                "current_book": current_book,
                "current_reading": current_reading,
            }
        )

    return {
        "clubs": clubs,
    }
