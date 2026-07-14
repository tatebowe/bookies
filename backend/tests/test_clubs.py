def test_create_club(client, auth_headers):
    response = client.post(
        "/clubs/",
        headers=auth_headers,
        json={
            "name": "Test Book Club",
            "description": "A club for testing",
            "is_public": True,
            "join_policy": "open",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Book Club"
    assert data["description"] == "A club for testing"
    assert data["is_public"] is True
    assert data["join_policy"] == "open"


def test_create_club_requires_auth(client):
    response = client.post(
        "/clubs/",
        json={
            "name": "Unauthorized Club",
            "description": "Should fail",
        },
    )

    assert response.status_code == 401


def test_get_my_clubs(client, auth_headers):
    create_response = client.post(
        "/clubs/",
        headers=auth_headers,
        json={
            "name": "My Club",
            "description": "My test club",
        },
    )

    assert create_response.status_code == 200

    response = client.get(
        "/clubs/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    clubs = response.json()

    assert len(clubs) == 1
    assert clubs[0]["name"] == "My Club"


def test_get_my_clubs_empty(client, auth_headers):
    response = client.get(
        "/clubs/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_club_members(client, auth_headers):
    create_response = client.post(
        "/clubs/",
        headers=auth_headers,
        json={
            "name": "Member Test Club",
            "description": "Testing members",
        },
    )

    assert create_response.status_code == 200

    club = create_response.json()

    response = client.get(
        f"/clubs/{club['id']}/members",
        headers=auth_headers,
    )

    assert response.status_code == 200

    members = response.json()

    assert len(members) == 1
    assert members[0]["username"] == "testuser"
    assert members[0]["email"] == "test@example.com"
