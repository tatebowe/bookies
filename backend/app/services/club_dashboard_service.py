from sqlalchemy.orm import Session

from app.exceptions.permission_exceptions import NotClubMemberError
from app.models.book import Book
from app.models.club import Club
from app.models.club_reading import ClubReading
from app.models.discussion_note import DiscussionNote
from app.models.membership import ClubMembership
from app.models.voting_cycle import VotingCycle
from app.services.helpers import get_by_id


def get_club_dashboard(
    db: Session,
    club_id: int,
    user_id: int,
):
    """
    Return dashboard data for a club.

    User must be a club member.
    """

    membership = (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
            ClubMembership.user_id == user_id,
        )
        .first()
    )

    if membership is None:
        raise NotClubMemberError("User is not a member of this club")

    club = get_by_id(
        db,
        Club,
        club_id,
    )

    active_cycle = (
        db.query(VotingCycle)
        .filter(
            VotingCycle.club_id == club_id,
            VotingCycle.active.is_(True),
        )
        .first()
    )

    current_book = None

    if active_cycle and active_cycle.selected_book_id:
        current_book = get_by_id(
            db,
            Book,
            active_cycle.selected_book_id,
        )

    readings = []

    if active_cycle:
        readings = (
            db.query(ClubReading)
            .filter(
                ClubReading.club_id == club_id,
                ClubReading.cycle_id == active_cycle.id,
            )
            .all()
        )

    progress = {
        "not_started": 0,
        "reading": 0,
        "completed": 0,
    }

    members = []

    for reading in readings:
        progress[reading.status] += 1

        members.append(
            {
                "username": reading.user.username,
                "status": reading.status,
            }
        )

    discussion_count = (
        db.query(DiscussionNote)
        .join(
            ClubReading,
            DiscussionNote.club_reading_id == ClubReading.id,
        )
        .filter(
            ClubReading.club_id == club_id,
        )
        .count()
    )

    return {
        "club": club,
        "current_book": current_book,
        "reading_progress": progress,
        "members": members,
        "active_cycle": active_cycle,
        "discussion_notes_count": discussion_count,
    }
