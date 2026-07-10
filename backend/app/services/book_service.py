from sqlalchemy.orm import Session

from app.integrations.google_books import (
    search_books as google_search_books,
)
from app.models.book import Book
from app.schemas.book import BookSearchResult
from app.services.helpers import save_and_refresh


def search_books(
    query: str,
    max_results: int = 10,
) -> list[BookSearchResult]:
    """
    Search Google Books and return formatted results.
    """

    results = google_search_books(
        query,
        max_results,
    )

    return [BookSearchResult(**book) for book in results]


def get_book_by_google_id(
    db: Session,
    google_books_id: str,
) -> Book | None:
    """
    Find an existing book by Google Books ID.
    """

    return db.query(Book).filter(Book.google_books_id == google_books_id).first()


def create_book(
    db: Session,
    book_data: BookSearchResult,
) -> Book:
    """
    Save a book if it does not already exist.
    """

    existing_book = get_book_by_google_id(
        db,
        book_data.google_books_id,
    )

    if existing_book:
        return existing_book

    new_book = Book(
        google_books_id=book_data.google_books_id,
        title=book_data.title,
        authors=book_data.authors,
        description=book_data.description,
        isbn=book_data.isbn,
        published_date=book_data.published_date,
        page_count=book_data.page_count,
        language=book_data.language,
        categories=book_data.categories,
        thumbnail_url=book_data.thumbnail_url,
    )

    return save_and_refresh(
        db,
        new_book,
    )
