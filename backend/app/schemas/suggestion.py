from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookSuggestionCreate(BaseModel):
    book_id: int
    anonymous: bool = True


class BookSuggestionResponse(BaseModel):
    id: int

    club_id: int
    book_id: int

    anonymous: bool

    created_at: datetime

    vote_count: int = 0

    model_config = ConfigDict(
        from_attributes=True,
    )
