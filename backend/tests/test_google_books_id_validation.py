"""A volume ID is interpolated into an outbound URL path, so it must be opaque.

Left unchecked, "../../../oauth2/v3/userinfo" walks out of /books/v1/volumes
and reaches an unrelated googleapis.com endpoint with our API key attached.
"""

import httpx
import pytest
from app.exceptions.book_exceptions import InvalidGoogleBooksIdError
from app.integrations import google_books

TRAVERSAL_IDS = [
    "../../../oauth2/v3/userinfo",
    "..%2F..%2Foauth2",
    "abc/../../../etc",
    "abc?key=leak",
    "abc#fragment",
    "abc def",
    "",
]


def register(client, username="reader", email="reader@example.com"):
    response = client.post(
        "/users/",
        json={
            "username": username,
            "email": email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    ).json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("volume_id", TRAVERSAL_IDS)
def test_api_rejects_unsafe_volume_ids(client, volume_id, monkeypatch):
    """The request must be refused before any outbound call happens."""
    calls = []

    def fail_if_called(url, params=None, timeout=None):
        calls.append(url)
        raise AssertionError(f"outbound request should not happen: {url}")

    monkeypatch.setattr(google_books.httpx, "get", fail_if_called)

    headers = register(client)

    response = client.post(
        "/books/",
        headers=headers,
        json={"google_books_id": volume_id},
    )

    assert response.status_code in (400, 422)
    assert calls == []


@pytest.mark.parametrize("volume_id", TRAVERSAL_IDS)
def test_integration_layer_refuses_unsafe_volume_ids(volume_id):
    """Backstop: the guard lives where the URL is built, not only at the API."""
    with pytest.raises(InvalidGoogleBooksIdError):
        google_books.get_google_book_by_id(volume_id)


def test_valid_volume_id_still_reaches_the_volumes_endpoint(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured["url"] = url
        return httpx.Response(
            200,
            json={"id": "zyTCAlFPjgYC", "volumeInfo": {"title": "A Book"}},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(google_books.httpx, "get", fake_get)

    book = google_books.get_google_book_by_id("zyTCAlFPjgYC")

    assert captured["url"] == (
        "https://www.googleapis.com/books/v1/volumes/zyTCAlFPjgYC"
    )
    assert book["title"] == "A Book"


def test_hyphen_and_underscore_ids_are_allowed(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return httpx.Response(
            200,
            json={"id": "a-b_C9", "volumeInfo": {"title": "Hyphenated"}},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(google_books.httpx, "get", fake_get)

    assert google_books.get_google_book_by_id("a-b_C9")["title"] == "Hyphenated"
