from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReadingEntryCreate(BaseModel):
    book_id: int


class ReadingEntryStatusUpdate(BaseModel):
    status: str


class ReadingEntryReviewUpdate(BaseModel):
    rating: float | None = None
    review: str | None = None


class ReadingEntryResponse(BaseModel):
    id: int

    user_id: int
    book_id: int

    status: str

    rating: float | None
    review: str | None

    started_at: datetime | None
    finished_at: datetime | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
