from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClubReadingStatusUpdate(BaseModel):
    status: str


class ClubReadingReviewUpdate(BaseModel):
    rating: float | None = None
    review: str | None = None


class ClubReadingResponse(BaseModel):
    id: int

    club_id: int
    cycle_id: int
    book_id: int
    user_id: int

    status: str

    rating: float | None
    review: str | None

    started_at: datetime | None
    finished_at: datetime | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
