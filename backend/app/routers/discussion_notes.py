from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.discussion_note import (
    DiscussionNoteCreate,
    DiscussionNoteResponse,
    DiscussionNoteUpdate,
)
from app.services.discussion_note_service import (
    create_discussion_note,
    delete_discussion_note,
    get_discussion_note_by_id,
    get_discussion_notes,
    update_discussion_note,
)

router = APIRouter(
    prefix="/clubs/readings",
    tags=["Discussion Notes"],
)


@router.post(
    "/{reading_id}/notes",
    response_model=DiscussionNoteResponse,
)
def create_note(
    reading_id: int,
    note: DiscussionNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_discussion_note(
        db,
        reading_id,
        current_user.id,
        note.title,
        note.content,
    )


@router.get(
    "/{reading_id}/notes",
    response_model=list[DiscussionNoteResponse],
)
def list_notes(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_discussion_notes(
        db,
        reading_id,
        current_user.id,
    )


@router.patch(
    "/notes/{note_id}",
    response_model=DiscussionNoteResponse,
)
def update_note(
    note_id: int,
    update: DiscussionNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_discussion_note_by_id(
        db,
        note_id,
        current_user.id,
    )

    return update_discussion_note(
        db,
        note,
        update.title,
        update.content,
    )


@router.delete(
    "/notes/{note_id}",
)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_discussion_note_by_id(
        db,
        note_id,
        current_user.id,
    )

    delete_discussion_note(
        db,
        note,
    )

    return {
        "message": "Discussion note deleted",
    }
