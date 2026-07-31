"""Membership and lookup failures must surface as 403/404, never as a 500."""

from app.exceptions.permission_exceptions import (
    NotClubMemberError as PermissionNotClubMemberError,
)
from app.exceptions.suggestion_exceptions import (
    NotClubMemberError as SuggestionNotClubMemberError,
)


def register(client, username, email, password="password123"):
    response = client.post(
        "/users/",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    ).json()["access_token"]

    return response.json(), {"Authorization": f"Bearer {token}"}


def test_not_club_member_error_is_a_single_class():
    assert SuggestionNotClubMemberError is PermissionNotClubMemberError


def test_non_member_suggestion_returns_403(client, mock_google_book):
    _, owner_headers = register(client, "owner", "owner@example.com")

    club = client.post(
        "/clubs/",
        headers=owner_headers,
        json={
            "name": "Handler Club",
            "is_public": True,
        },
    ).json()

    book = client.post(
        "/books/",
        headers=owner_headers,
        json={"google_books_id": "the-hobbit-test-id"},
    ).json()

    _, outsider_headers = register(client, "outsider", "outsider@example.com")

    response = client.post(
        f"/clubs/{club['id']}/suggestions",
        headers=outsider_headers,
        json={
            "book_id": book["id"],
            "anonymous": False,
        },
    )

    assert response.status_code == 403


def test_joining_a_missing_club_returns_404(client):
    _, headers = register(client, "joiner", "joiner@example.com")

    response = client.post(
        "/clubs/999999/join",
        headers=headers,
    )

    assert response.status_code == 404
