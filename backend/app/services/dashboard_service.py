from sqlalchemy.orm import Session

from app.models.club_reading import ClubReading
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

    reading_entries = (
        db.query(ReadingEntry)
        .filter(
            ReadingEntry.user_id == user_id,
            ReadingEntry.status != "completed",
        )
        .all()
    )

    current_readings = []
    for entry in reading_entries:
        club_reading = (
            db.query(ClubReading)
            .filter(ClubReading.reading_entry_id == entry.id)
            .first()
        )
        current_readings.append(
            {
                "id": entry.id,
                "status": entry.status,
                "rating": entry.rating,
                "review": entry.review,
                "book": entry.book,
                "club": club_reading.club if club_reading else None,
                "club_reading_id": club_reading.id if club_reading else None,
            }
        )

    history_entries = (
        db.query(ReadingEntry)
        .filter(
            ReadingEntry.user_id == user_id,
            ReadingEntry.status == "completed",
        )
        .all()
    )

    history = []
    for entry in history_entries:
        club_reading = (
            db.query(ClubReading)
            .filter(ClubReading.reading_entry_id == entry.id)
            .first()
        )
        history.append(
            {
                "id": entry.id,
                "status": entry.status,
                "rating": entry.rating,
                "review": entry.review,
                "book": entry.book,
                "club": club_reading.club if club_reading else None,
            }
        )

    user_notes = (
        db.query(ReadingNote)
        .filter(
            ReadingNote.user_id == user_id,
        )
        .all()
    )

    notes = []
    for note in user_notes:
        book = None
        if note.reading_entry is not None:
            book = note.reading_entry.book
        elif note.club_reading is not None:
            book = note.club_reading.book
        notes.append(
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at,
                "book": book,
            }
        )

    return {
        "profile": user,
        "clubs": clubs,
        "current_readings": current_readings,
        "history": history,
        "notes": notes,
    }
