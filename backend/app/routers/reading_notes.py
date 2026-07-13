from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.reading_note import (
    ReadingNoteCreate,
    ReadingNoteResponse,
    ReadingNoteUpdate,
)
from app.services.reading_note_service import (
    create_reading_note,
    delete_reading_note,
    get_notes_for_club_reading,
    get_notes_for_entry,
    get_reading_note,
    get_user_notes,
    update_reading_note,
)

router = APIRouter(
    prefix="/reading-notes",
    tags=["Reading Notes"],
)


@router.post(
    "/",
    response_model=ReadingNoteResponse,
)
def create_note(
    note: ReadingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_reading_note(
        db,
        current_user.id,
        note.content,
        note.title,
        note.reading_entry_id,
        note.club_reading_id,
    )


@router.get(
    "/",
    response_model=list[ReadingNoteResponse],
)
def list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_notes(
        db,
        current_user.id,
    )


@router.get(
    "/entry/{reading_entry_id}",
    response_model=list[ReadingNoteResponse],
)
def list_entry_notes(
    reading_entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_notes_for_entry(
        db,
        reading_entry_id,
        current_user.id,
    )


@router.get(
    "/club-reading/{club_reading_id}",
    response_model=list[ReadingNoteResponse],
)
def list_club_reading_notes(
    club_reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_notes_for_club_reading(
        db,
        club_reading_id,
        current_user.id,
    )


@router.patch(
    "/{note_id}",
    response_model=ReadingNoteResponse,
)
def update_note(
    note_id: int,
    update: ReadingNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_reading_note(
        db,
        note_id,
        current_user.id,
    )

    return update_reading_note(
        db,
        note,
        update.title,
        update.content,
    )


@router.delete(
    "/{note_id}",
)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_reading_note(
        db,
        note_id,
        current_user.id,
    )

    delete_reading_note(
        db,
        note,
    )

    return {
        "message": "Reading note deleted",
    }
