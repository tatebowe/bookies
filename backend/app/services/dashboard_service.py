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

    club_readings = db.query(ClubReading).filter(ClubReading.user_id == user_id).all()
    needs_sync = False
    for club_reading in club_readings:
        entry = club_reading.reading_entry
        if entry is None:
            continue
        if entry.status != club_reading.status:
            entry.status = club_reading.status
            entry.started_at = club_reading.started_at or entry.started_at
            entry.finished_at = club_reading.finished_at or entry.finished_at
            needs_sync = True
        if club_reading.rating is not None and entry.rating != club_reading.rating:
            entry.rating = club_reading.rating
            needs_sync = True
        if club_reading.review is not None and entry.review != club_reading.review:
            entry.review = club_reading.review
            needs_sync = True
    if needs_sync:
        db.commit()

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
                "finished_at": entry.finished_at,
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
                "finished_at": entry.finished_at,
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
