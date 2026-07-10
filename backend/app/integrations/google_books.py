import time

import httpx

from app.core.config import settings

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


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
