"""Book search spends our Google Books quota, so it needs a caller we know.

Upstream trouble must also arrive as a 503, not as a 500 with a traceback.
"""

import httpx
import pytest
from app.exceptions.book_exceptions import BookLookupUnavailableError
from app.integrations import google_books


def auth_headers(client, username="reader", email="reader@example.com"):
    assert (
        client.post(
            "/users/",
            json={
                "username": username,
                "email": email,
                "password": "password123",
            },
        ).status_code
        == 200
    )

    token = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    ).json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def respond(status_code, json_body=None):
    def fake_get(url, params=None, timeout=None):
        return httpx.Response(
            status_code,
            json=json_body if json_body is not None else {},
            request=httpx.Request("GET", url),
        )

    return fake_get


# --- authentication -------------------------------------------------------


def test_search_requires_authentication(client, monkeypatch):
    calls = []

    def fail_if_called(url, params=None, timeout=None):
        calls.append(url)
        raise AssertionError("anonymous search must not reach Google Books")

    monkeypatch.setattr(google_books.httpx, "get", fail_if_called)

    response = client.get("/books/search?q=Test")

    assert response.status_code == 401
    assert calls == []


def test_search_works_when_authenticated(client, monkeypatch):
    monkeypatch.setattr(
        google_books.httpx,
        "get",
        respond(200, {"items": [{"id": "abc", "volumeInfo": {"title": "A Book"}}]}),
    )

    response = client.get("/books/search?q=Test", headers=auth_headers(client))

    assert response.status_code == 200
    assert response.json()[0]["title"] == "A Book"


# --- upstream failures map to 503 ----------------------------------------


def test_rate_limited_search_returns_503(client, monkeypatch):
    monkeypatch.setattr(google_books, "RATE_LIMIT_RETRY_SECONDS", 0)
    monkeypatch.setattr(google_books.httpx, "get", respond(429))

    response = client.get("/books/search?q=Test", headers=auth_headers(client))

    assert response.status_code == 503
    assert "rate limiting" in response.json()["detail"]


def test_upstream_server_error_returns_503(client, monkeypatch):
    monkeypatch.setattr(google_books.httpx, "get", respond(500))

    response = client.get("/books/search?q=Test", headers=auth_headers(client))

    assert response.status_code == 503


def test_network_failure_returns_503(client, monkeypatch):
    def boom(url, params=None, timeout=None):
        raise httpx.ConnectError("no route to host")

    monkeypatch.setattr(google_books.httpx, "get", boom)

    response = client.get("/books/search?q=Test", headers=auth_headers(client))

    assert response.status_code == 503


def test_rate_limit_is_retried_once(monkeypatch):
    monkeypatch.setattr(google_books, "RATE_LIMIT_RETRY_SECONDS", 0)

    attempts = []

    def flaky(url, params=None, timeout=None):
        attempts.append(url)
        status = 429 if len(attempts) == 1 else 200
        return httpx.Response(
            status,
            json={"items": []},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(google_books.httpx, "get", flaky)

    assert google_books.search_books("anything") == []
    assert len(attempts) == 2


def test_saving_a_book_also_maps_upstream_failure(monkeypatch):
    monkeypatch.setattr(google_books, "RATE_LIMIT_RETRY_SECONDS", 0)
    monkeypatch.setattr(google_books.httpx, "get", respond(429))

    with pytest.raises(BookLookupUnavailableError):
        google_books.get_google_book_by_id("zyTCAlFPjgYC")
