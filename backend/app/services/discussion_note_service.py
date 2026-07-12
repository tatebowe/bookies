from sqlalchemy.orm import Session

from app.exceptions.discussion_note_exceptions import (
    DiscussionNoteNotFoundError,
    UnauthorizedDiscussionNoteError,
)
from app.models.club_reading import ClubReading
from app.models.discussion_note import DiscussionNote
from app.services.helpers import get_by_id, save_and_refresh


def get_user_club_reading(
    db: Session,
    club_reading_id: int,
    user_id: int,
) -> ClubReading:
    """
    Retrieve a club reading belonging to a user.

    Raises:
        UnauthorizedDiscussionNoteError:
            If the reading does not belong to the user.
    """

    reading = get_by_id(
        db,
        ClubReading,
        club_reading_id,
    )

    if reading is None or reading.user_id != user_id:
        raise UnauthorizedDiscussionNoteError(
            "Reading not found or user is not authorized"
        )

    return reading


def create_discussion_note(
    db: Session,
    club_reading_id: int,
    user_id: int,
    title: str | None,
    content: str,
) -> DiscussionNote:
    """
    Create a private discussion note for a user's reading.
    """

    get_user_club_reading(
        db,
        club_reading_id,
        user_id,
    )

    note = DiscussionNote(
        club_reading_id=club_reading_id,
        title=title,
        content=content,
    )

    return save_and_refresh(
        db,
        note,
    )


def get_discussion_notes(
    db: Session,
    club_reading_id: int,
    user_id: int,
) -> list[DiscussionNote]:
    """
    Return all notes for a user's reading.
    """

    get_user_club_reading(
        db,
        club_reading_id,
        user_id,
    )

    return (
        db.query(DiscussionNote)
        .filter(
            DiscussionNote.club_reading_id == club_reading_id,
        )
        .all()
    )


def get_discussion_note_by_id(
    db: Session,
    note_id: int,
    user_id: int,
) -> DiscussionNote:
    """
    Retrieve one note owned by the user.
    """

    note = get_by_id(
        db,
        DiscussionNote,
        note_id,
    )

    if note is None:
        raise DiscussionNoteNotFoundError("Discussion note not found")

    reading = get_by_id(
        db,
        ClubReading,
        note.club_reading_id,
    )

    if reading is None or reading.user_id != user_id:
        raise UnauthorizedDiscussionNoteError(
            "User is not authorized to access this note"
        )

    return note


def update_discussion_note(
    db: Session,
    note: DiscussionNote,
    title: str | None,
    content: str | None,
) -> DiscussionNote:
    """
    Update a discussion note.
    """

    if title is not None:
        note.title = title

    if content is not None:
        note.content = content

    return save_and_refresh(
        db,
        note,
    )


def delete_discussion_note(
    db: Session,
    note: DiscussionNote,
) -> None:
    """
    Delete a discussion note.
    """

    db.delete(note)
    db.commit()
