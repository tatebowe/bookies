from sqlalchemy.orm import Session

from app.exceptions.permission_exceptions import NotClubMemberError
from app.models.book import Book
from app.models.club import Club
from app.models.club_reading import ClubReading
from app.models.discussion_note import DiscussionNote
from app.models.membership import ClubMembership
from app.models.suggestion import BookSuggestion
from app.models.voting_cycle import VotingCycle
from app.services.helpers import get_by_id
from app.services.voting_cycle_service import get_open_participation_cycle


def get_club_dashboard(
    db: Session,
    club_id: int,
    user_id: int,
):
    """
    Return dashboard data for a club.

    Public clubs can be browsed by signed-in readers; private clubs require membership.
    """

    club = get_by_id(
        db,
        Club,
        club_id,
    )

    membership = (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
            ClubMembership.user_id == user_id,
        )
        .first()
    )

    if membership is None and not club.is_public:
        raise NotClubMemberError("User is not a member of this club")

    active_cycle = (
        db.query(VotingCycle)
        .filter(
            VotingCycle.club_id == club_id,
            VotingCycle.active.is_(True),
        )
        .first()
    )

    future_cycles = (
        db.query(VotingCycle)
        .filter(
            VotingCycle.club_id == club_id,
            VotingCycle.active.is_(False),
            VotingCycle.phase == "suggestion",
        )
        .order_by(VotingCycle.suggestion_start_date)
        .all()
    )
    participation_cycle = get_open_participation_cycle(db, club_id)

    current_book = None

    if active_cycle and active_cycle.selected_book_id:
        current_book = get_by_id(
            db,
            Book,
            active_cycle.selected_book_id,
        )
        winning_suggestion = (
            db.query(BookSuggestion)
            .filter(
                BookSuggestion.club_id == club_id,
                BookSuggestion.cycle_id == active_cycle.id,
                BookSuggestion.book_id == active_cycle.selected_book_id,
            )
            .first()
        )
        if winning_suggestion and current_book:
            current_book.suggested_by_display_name = (
                winning_suggestion.suggested_by.display_name
                or winning_suggestion.suggested_by.username
            )

    readings = []
    viewer_club_reading_id = None

    if active_cycle:
        readings = (
            db.query(ClubReading)
            .filter(
                ClubReading.club_id == club_id,
                ClubReading.cycle_id == active_cycle.id,
            )
            .all()
        )
        viewer_reading = next(
            (reading for reading in readings if reading.user_id == user_id), None
        )
        viewer_club_reading_id = viewer_reading.id if viewer_reading else None

    progress = {
        "not_started": 0,
        "reading": 0,
        "completed": 0,
    }

    members = []

    for reading in readings:
        progress[reading.status] += 1

    memberships = (
        db.query(ClubMembership)
        .filter(
            ClubMembership.club_id == club_id,
        )
        .all()
    )

    members = []

    for member_membership in memberships:
        members.append(
            {
                "username": member_membership.user.username,
                "display_name": member_membership.user.display_name,
                "role": member_membership.role,
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
        "active_cycle": (
            {
                **active_cycle.__dict__,
                "selected_book": current_book,
            }
            if active_cycle
            else None
        ),
        "participation_cycle": participation_cycle,
        "future_cycles": future_cycles,
        "discussion_notes_count": discussion_count,
        "viewer_role": membership.role if membership else "",
        "viewer_club_reading_id": viewer_club_reading_id,
    }
