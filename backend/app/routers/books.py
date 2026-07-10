from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.book import (
    BookResponse,
    BookSearchResult,
)
from app.services.book_service import (
    create_book,
    search_books,
)

router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


@router.get(
    "/search",
    response_model=list[BookSearchResult],
)
def search_for_books(
    q: str,
):
    """
    Search Google Books.
    """

    return search_books(q)


@router.post(
    "/",
    response_model=BookResponse,
)
def save_book(
    book: BookSearchResult,
    db: Session = Depends(get_db),
):
    """
    Save a book to the global book library.
    """

    return create_book(
        db,
        book,
    )
