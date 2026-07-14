from sqlalchemy.orm import Session

from app.models.membership import ClubMembership
from app.models.reading_entry import ReadingEntry
from app.models.reading_note import ReadingNote
from app.models.user import User
from app.models.voting_cycle import VotingCycle


def get_user_dashboard(
    db: Session,
    user_id: int,
):

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
        )
        .first()
    )

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

        clubs.append(
            {
                "club": club,
                "role": membership.role,
                "active_cycle": active_cycle,
            }
        )

    current_readings = (
        db.query(ReadingEntry)
        .filter(
            ReadingEntry.user_id == user_id,
            ReadingEntry.status.in_(
                [
                    "reading",
                    "started",
                ]
            ),
        )
        .all()
    )

    history = (
        db.query(ReadingEntry)
        .filter(
            ReadingEntry.user_id == user_id,
            ReadingEntry.status == "completed",
        )
        .all()
    )

    notes = (
        db.query(ReadingNote)
        .filter(
            ReadingNote.user_id == user_id,
        )
        .all()
    )

    return {
        "profile": user,
        "clubs": clubs,
        "current_readings": current_readings,
        "history": history,
        "notes": notes,
    }
