from sqlalchemy.orm import Session

from app.models.club_reading import ClubReading
from app.models.membership import ClubMembership
from app.models.voting_cycle import VotingCycle


def get_user_dashboard(
    db: Session,
    user_id: int,
):

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
                "active_cycle": active_cycle,
            }
        )

    current_readings = (
        db.query(ClubReading)
        .filter(
            ClubReading.user_id == user_id,
            ClubReading.status.in_(
                [
                    "reading",
                    "started",
                ]
            ),
        )
        .all()
    )

    history = (
        db.query(ClubReading)
        .filter(
            ClubReading.user_id == user_id,
            ClubReading.status == "completed",
        )
        .all()
    )

    return {
        "current_readings": current_readings,
        "clubs": clubs,
        "history": history,
    }
