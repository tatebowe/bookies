import re
import time

import httpx

from app.core.config import settings
from app.exceptions.book_exceptions import InvalidGoogleBooksIdError
from app.schemas.book import GOOGLE_BOOKS_ID_PATTERN

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

VOLUME_ID_RE = re.compile(GOOGLE_BOOKS_ID_PATTERN)


def search_books(
    query: str,
    max_results: int = 10,
) -> list[dict]:

    params = {
        "q": query,
        "maxResults": max_results,
    }

    if settings.google_books_api_key:
        params["key"] = settings.google_books_api_key

    response = httpx.get(
        GOOGLE_BOOKS_URL,
        params=params,
        timeout=10,
    )

    # Retry once if Google rate limits us
    if response.status_code == 429:
        time.sleep(2)

        response = httpx.get(
            GOOGLE_BOOKS_URL,
            params=params,
            timeout=10,
        )

    response.raise_for_status()

    data = response.json()

    return [parse_book(item) for item in data.get("items", [])]


def get_google_book_by_id(
    google_books_id: str,
) -> dict:
    """
    Retrieve a single book from Google Books by volume ID.

    Raises:
        InvalidGoogleBooksIdError:
            If the ID is not an opaque alphanumeric token. It is interpolated
            into the request path, so a value containing "../" would walk out
            of /books/v1/volumes and reach an unrelated googleapis.com
            endpoint with our API key attached.
    """

    if not VOLUME_ID_RE.fullmatch(google_books_id):
        raise InvalidGoogleBooksIdError(
            f"Invalid Google Books volume ID: {google_books_id!r}",
        )

    url = f"{GOOGLE_BOOKS_URL}/{google_books_id}"

    params = {}

    if settings.google_books_api_key:
        params["key"] = settings.google_books_api_key

    response = httpx.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return parse_book(
        response.json(),
    )


def parse_book(
    item: dict,
) -> dict:

    volume = item.get(
        "volumeInfo",
        {},
    )

    return {
        "google_books_id": item.get("id"),
        "title": volume.get("title"),
        "authors": extract_authors(volume),
        "description": volume.get("description"),
        "isbn": extract_isbn(volume),
        "published_date": volume.get("publishedDate"),
        "page_count": volume.get("pageCount"),
        "language": volume.get("language"),
        "categories": extract_categories(volume),
        "thumbnail_url": (volume.get("imageLinks", {}).get("thumbnail")),
    }


def extract_authors(
    volume_info: dict,
) -> str | None:

    authors = volume_info.get(
        "authors",
        [],
    )

    if not authors:
        return None

    return ", ".join(authors)


def extract_categories(
    volume_info: dict,
) -> str | None:

    categories = volume_info.get(
        "categories",
        [],
    )

    if not categories:
        return None

    return ", ".join(categories)


def extract_isbn(
    volume_info: dict,
) -> str | None:

    for identifier in volume_info.get(
        "industryIdentifiers",
        [],
    ):
        if identifier.get("type") == "ISBN_13":
            return identifier.get("identifier")

    return None
