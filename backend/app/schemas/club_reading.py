from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClubReadingStatusUpdate(BaseModel):
    status: Literal[
        "not_started",
        "reading",
        "completed",
    ]


class ClubReadingReviewUpdate(BaseModel):

    rating: float | None = Field(
        default=None,
        ge=0.5,
        le=5,
    )

    review: str | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value):
        if value is not None and value % 0.5 != 0:
            raise ValueError("Rating must be in half-star increments")

        return value


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
