from sqlalchemy.orm import Session

from app.exceptions.reading_note_exceptions import (
    ReadingNoteNotFoundError,
    UnauthorizedReadingNoteError,
)
from app.models.reading_note import ReadingNote
from app.services.helpers import get_by_id, save_and_refresh


def create_reading_note(
    db: Session,
    user_id: int,
    content: str,
    title: str | None = None,
    reading_entry_id: int | None = None,
    club_reading_id: int | None = None,
) -> ReadingNote:

    if reading_entry_id is None and club_reading_id is None:
        raise ValueError("Reading note must belong to a reading entry or club reading")

    note = ReadingNote(
        user_id=user_id,
        title=title,
        content=content,
        reading_entry_id=reading_entry_id,
        club_reading_id=club_reading_id,
    )

    return save_and_refresh(
        db,
        note,
    )


def get_reading_note(
    db: Session,
    note_id: int,
    user_id: int,
) -> ReadingNote:

    note = get_by_id(
        db,
        ReadingNote,
        note_id,
    )

    if note is None:
        raise ReadingNoteNotFoundError("Reading note not found")

    if note.user_id != user_id:
        raise UnauthorizedReadingNoteError("User does not own this note")

    return note


def get_user_notes(
    db: Session,
    user_id: int,
) -> list[ReadingNote]:

    return (
        db.query(ReadingNote)
        .filter(
            ReadingNote.user_id == user_id,
        )
        .all()
    )


def get_notes_for_entry(
    db: Session,
    reading_entry_id: int,
    user_id: int,
) -> list[ReadingNote]:

    return (
        db.query(ReadingNote)
        .filter(
            ReadingNote.reading_entry_id == reading_entry_id,
            ReadingNote.user_id == user_id,
        )
        .all()
    )


def get_notes_for_club_reading(
    db: Session,
    club_reading_id: int,
    user_id: int,
) -> list[ReadingNote]:

    return (
        db.query(ReadingNote)
        .filter(
            ReadingNote.club_reading_id == club_reading_id,
            ReadingNote.user_id == user_id,
        )
        .all()
    )


def update_reading_note(
    db: Session,
    note: ReadingNote,
    title: str | None,
    content: str | None,
) -> ReadingNote:

    if title is not None:
        note.title = title

    if content is not None:
        note.content = content

    return save_and_refresh(
        db,
        note,
    )


def delete_reading_note(
    db: Session,
    note: ReadingNote,
) -> None:

    db.delete(note)
    db.commit()
