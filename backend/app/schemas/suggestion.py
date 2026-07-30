from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookSummary(BaseModel):
    id: int
    title: str
    authors: str | None
    description: str | None = None
    thumbnail_url: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class BookSuggestionCreate(BaseModel):
    book_id: int
    anonymous: bool = True


class BookSuggestionResponse(BaseModel):
    id: int
    club_id: int
    anonymous: bool
    created_at: datetime

    book: BookSummary

    vote_count: int = 0
    can_view_vote_totals: bool = False

    model_config = ConfigDict(
        from_attributes=True,
    )
