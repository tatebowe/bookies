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
    authors: str | None = None
    description: str | None = None
    isbn: str | None = None
    published_date: str | None = None
    page_count: int | None = None
    language: str | None = None
    categories: str | None = None
    thumbnail_url: str | None = None


class BookCreate(BaseModel):
    google_books_id: str
