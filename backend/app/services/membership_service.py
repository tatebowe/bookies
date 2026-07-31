from sqlalchemy.orm import Session

from app.models.membership import ClubMembership
from app.services.club_reading_service import create_reading_for_member
from app.services.helpers import save_and_refresh
from app.services.voting_cycle_service import get_active_cycle


def add_current_reading_if_available(
    db: Session,
    club_id: int,
    user_id: int,
) -> None:
    """
    If the club currently has an active reading cycle,
    create a reading record for the new member.
    """

    cycle = get_active_cycle(
        db,
        club_id,
    )

    if cycle and cycle.phase == "reading" and cycle.selected_book_id:
        create_reading_for_member(
            db,
            club_id,
            cycle.id,
            cycle.selected_book_id,
            user_id,
        )


def grant_membership(
    db: Session,
    club_id: int,
    user_id: int,
    role: str = "member",
) -> ClubMembership:
    """
    Add a user to a club and hook them into the current reading.

    Every path that creates a membership goes through here. Skipping the
    reading hookup would leave the new member absent from reading progress
    for the cycle already under way.
    """

    membership = ClubMembership(
        club_id=club_id,
        user_id=user_id,
        role=role,
    )

    save_and_refresh(
        db,
        membership,
    )

    add_current_reading_if_available(
        db,
        club_id,
        user_id,
    )

    return membership
