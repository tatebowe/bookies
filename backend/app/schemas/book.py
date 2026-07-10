from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookResponse(BaseModel):
    id: int
    google_books_id: str
    title: str
    authors: str | None
    description: str | None
    isbn: str | None
    published_date: str | None
    page_count: int | None
    language: str | None
    categories: str | None
    thumbnail_url: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class BookSearchResult(BaseModel):
    google_books_id: str
    title: str
    authors: str | None
    description: str | None
    isbn: str | None
    published_date: str | None
    page_count: int | None
    language: str | None
    categories: str | None
    thumbnail_url: str | None
