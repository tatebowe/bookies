"""An unknown club id must be a 404, not an unhandled AttributeError."""


def auth_for(client, username, email):
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


def test_dashboard_for_missing_club_returns_404(client):
    headers = auth_for(client, "reader", "reader@example.com")

    response = client.get("/clubs/999999/dashboard", headers=headers)

    assert response.status_code == 404


def test_dashboard_for_private_club_still_returns_403_for_non_members(client):
    owner_headers = auth_for(client, "owner", "owner@example.com")

    club = client.post(
        "/clubs/",
        headers=owner_headers,
        json={
            "name": "Private Club",
            "is_public": False,
            "join_policy": "invite",
        },
    ).json()

    outsider_headers = auth_for(client, "outsider", "outsider@example.com")

    response = client.get(
        f"/clubs/{club['id']}/dashboard",
        headers=outsider_headers,
    )

    assert response.status_code == 403


def test_dashboard_still_works_for_members(client):
    owner_headers = auth_for(client, "owner", "owner@example.com")

    club = client.post(
        "/clubs/",
        headers=owner_headers,
        json={
            "name": "Private Club",
            "is_public": False,
            "join_policy": "invite",
        },
    ).json()

    response = client.get(
        f"/clubs/{club['id']}/dashboard",
        headers=owner_headers,
    )

    assert response.status_code == 200
    assert response.json()["club"]["name"] == "Private Club"
    assert response.json()["viewer_role"] == "owner"
