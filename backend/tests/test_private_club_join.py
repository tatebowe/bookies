"""A private club must never grant membership without a member's action.

is_public and join_policy are independent fields, so a private club left on
the "open" policy used to admit anyone who guessed its sequential id.
"""

import pytest


def auth(client, username, email):
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


def make_club(client, headers, name, is_public, join_policy):
    response = client.post(
        "/clubs/",
        headers=headers,
        json={
            "name": name,
            "is_public": is_public,
            "join_policy": join_policy,
        },
    )

    assert response.status_code == 200

    return response.json()


def club_names_for(client, headers):
    return [club["name"] for club in client.get("/clubs/", headers=headers).json()]


def test_private_open_club_does_not_admit_outsiders(client):
    owner = auth(client, "owner", "owner@example.com")
    club = make_club(client, owner, "Private Open", is_public=False, join_policy="open")

    outsider = auth(client, "outsider", "outsider@example.com")

    response = client.post(f"/clubs/{club['id']}/join", headers=outsider)

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert club_names_for(client, outsider) == []


def test_private_open_club_join_is_reviewable_by_the_owner(client):
    """Degraded to a request, not a hard rejection: the club stays usable."""
    owner = auth(client, "owner", "owner@example.com")
    club = make_club(client, owner, "Private Open", is_public=False, join_policy="open")

    outsider = auth(client, "outsider", "outsider@example.com")
    client.post(f"/clubs/{club['id']}/join", headers=outsider)

    pending = client.get(f"/clubs/{club['id']}/join-requests", headers=owner).json()

    assert len(pending) == 1

    approve = client.post(
        f"/clubs/join-requests/{pending[0]['id']}/approve",
        headers=owner,
    )

    assert approve.status_code == 200
    assert club_names_for(client, outsider) == ["Private Open"]


def test_public_open_club_still_admits_instantly(client):
    owner = auth(client, "owner", "owner@example.com")
    club = make_club(client, owner, "Public Open", is_public=True, join_policy="open")

    joiner = auth(client, "joiner", "joiner@example.com")

    response = client.post(f"/clubs/{club['id']}/join", headers=joiner)

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully joined club"
    assert club_names_for(client, joiner) == ["Public Open"]


@pytest.mark.parametrize("is_public", [True, False])
def test_request_policy_is_unchanged(client, is_public):
    owner = auth(client, "owner", "owner@example.com")
    club = make_club(client, owner, "Request Club", is_public, join_policy="request")

    outsider = auth(client, "outsider", "outsider@example.com")

    response = client.post(f"/clubs/{club['id']}/join", headers=outsider)

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert club_names_for(client, outsider) == []


@pytest.mark.parametrize("is_public", [True, False])
def test_invite_policy_is_unchanged(client, is_public):
    owner = auth(client, "owner", "owner@example.com")
    club = make_club(client, owner, "Invite Club", is_public, join_policy="invite")

    outsider = auth(client, "outsider", "outsider@example.com")

    response = client.post(f"/clubs/{club['id']}/join", headers=outsider)

    assert response.status_code == 400


def test_enumerating_private_club_ids_yields_no_memberships(client):
    """The original attack: walk the id space posting joins."""
    owner = auth(client, "owner", "owner@example.com")

    for index in range(5):
        make_club(
            client,
            owner,
            f"Secret {index}",
            is_public=False,
            join_policy="open",
        )

    attacker = auth(client, "attacker", "attacker@example.com")

    for club_id in range(1, 6):
        client.post(f"/clubs/{club_id}/join", headers=attacker)

    assert club_names_for(client, attacker) == []
