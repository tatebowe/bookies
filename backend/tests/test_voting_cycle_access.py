"""Who may read a club's active cycle.

This endpoint advances and persists cycle state, so it is restricted to
members even when the club itself is public.
"""

from datetime import datetime, timedelta, timezone


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


def make_club_with_cycle(client, headers, name, is_public):
    club = client.post(
        "/clubs/",
        headers=headers,
        json={
            "name": name,
            "is_public": is_public,
            "join_policy": "invite",
        },
    ).json()

    now = datetime.now(timezone.utc)

    cycle = client.post(
        f"/clubs/{club['id']}/cycles",
        headers=headers,
        json={
            "name": "Scheduled",
            "suggestion_start_date": now.isoformat(),
            "voting_start_date": (now + timedelta(days=2)).isoformat(),
            "voting_end_date": (now + timedelta(days=5)).isoformat(),
            "discussion_date": (now + timedelta(days=12)).isoformat(),
        },
    )

    assert cycle.status_code == 200

    return club


def test_active_cycle_requires_authentication(client):
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club_with_cycle(client, owner_headers, "Private", is_public=False)

    response = client.get(f"/clubs/{club['id']}/cycles/active")

    assert response.status_code == 401


def test_active_cycle_hidden_from_non_members_of_private_club(client):
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club_with_cycle(client, owner_headers, "Private", is_public=False)

    _, outsider_headers = register(client, "outsider", "outsider@example.com")

    response = client.get(
        f"/clubs/{club['id']}/cycles/active",
        headers=outsider_headers,
    )

    assert response.status_code == 403


def test_active_cycle_hidden_from_non_members_of_public_club(client):
    """Public clubs too: this endpoint writes, so browsing is not enough."""
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club_with_cycle(client, owner_headers, "Open", is_public=True)

    _, reader_headers = register(client, "reader", "reader@example.com")

    response = client.get(
        f"/clubs/{club['id']}/cycles/active",
        headers=reader_headers,
    )

    assert response.status_code == 403


def test_active_cycle_visible_to_members(client):
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club_with_cycle(client, owner_headers, "Private", is_public=False)

    response = client.get(
        f"/clubs/{club['id']}/cycles/active",
        headers=owner_headers,
    )

    assert response.status_code == 200
    assert response.json()["phase"] == "suggestion"


def test_anonymous_request_cannot_advance_cycle_state(client):
    """The unauthenticated caller must not reach the state machine at all."""
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club_with_cycle(client, owner_headers, "Private", is_public=False)

    before = client.get(
        f"/clubs/{club['id']}/cycles/active",
        headers=owner_headers,
    ).json()

    assert client.get(f"/clubs/{club['id']}/cycles/active").status_code == 401

    after = client.get(
        f"/clubs/{club['id']}/cycles/active",
        headers=owner_headers,
    ).json()

    assert before == after


def test_active_cycle_for_missing_club_returns_403(client):
    _, headers = register(client, "reader", "reader@example.com")

    response = client.get(
        "/clubs/999999/cycles/active",
        headers=headers,
    )

    assert response.status_code == 403
