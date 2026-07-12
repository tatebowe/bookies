from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.club_reading import (
    ClubReadingResponse,
    ClubReadingReviewUpdate,
    ClubReadingStatusUpdate,
)
from app.services.club_reading_service import (
    get_user_reading,
    update_reading_review,
    update_reading_status,
)

router = APIRouter(
    prefix="/readings",
    tags=["Club Readings"],
)


@router.get(
    "/{reading_id}",
    response_model=ClubReadingResponse,
)
def get_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = get_user_reading(
        db,
        reading_id,
    )

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail="Reading not found",
        )

    if reading.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this reading",
        )

    return reading


@router.patch(
    "/{reading_id}/status",
    response_model=ClubReadingResponse,
)
def update_status(
    reading_id: int,
    update: ClubReadingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = get_user_reading(
        db,
        reading_id,
    )

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail="Reading not found",
        )

    if reading.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this reading",
        )

    return update_reading_status(
        db,
        reading,
        update.status,
    )


@router.patch(
    "/{reading_id}/review",
    response_model=ClubReadingResponse,
)
def update_review(
    reading_id: int,
    review: ClubReadingReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = get_user_reading(
        db,
        reading_id,
    )

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail="Reading not found",
        )

    if reading.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this reading",
        )

    return update_reading_review(
        db,
        reading,
        review.rating,
        review.review,
    )
