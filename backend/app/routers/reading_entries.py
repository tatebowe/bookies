from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.reading_entry import (
    ReadingEntryCreate,
    ReadingEntryResponse,
    ReadingEntryReviewUpdate,
    ReadingEntryStatusUpdate,
)
from app.services.reading_entry_service import (
    create_reading_entry,
    get_reading_entry,
    get_user_reading_entries,
    update_reading_review,
    update_reading_status,
)

router = APIRouter(
    prefix="/reading-entries",
    tags=["Reading Entries"],
)


@router.post(
    "/",
    response_model=ReadingEntryResponse,
)
def create_entry(
    entry: ReadingEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_reading_entry(
        db,
        current_user.id,
        entry.book_id,
    )


@router.get(
    "/",
    response_model=list[ReadingEntryResponse],
)
def get_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_reading_entries(
        db,
        current_user.id,
    )


@router.get(
    "/{entry_id}",
    response_model=ReadingEntryResponse,
)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_reading_entry(
        db,
        entry_id,
        current_user.id,
    )


@router.patch(
    "/{entry_id}/status",
    response_model=ReadingEntryResponse,
)
def update_status(
    entry_id: int,
    update: ReadingEntryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = get_reading_entry(
        db,
        entry_id,
        current_user.id,
    )

    return update_reading_status(
        db,
        reading,
        update.status,
    )


@router.patch(
    "/{entry_id}/review",
    response_model=ReadingEntryResponse,
)
def update_review(
    entry_id: int,
    update: ReadingEntryReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = get_reading_entry(
        db,
        entry_id,
        current_user.id,
    )

    return update_reading_review(
        db,
        reading,
        update.rating,
        update.review,
    )
