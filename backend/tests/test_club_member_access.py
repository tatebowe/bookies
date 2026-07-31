"""Who may read a club's member roster, and what it may contain."""


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


def make_club(client, headers, name, is_public):
    response = client.post(
        "/clubs/",
        headers=headers,
        json={
            "name": name,
            "is_public": is_public,
            "join_policy": "invite",
        },
    )

    assert response.status_code == 200

    return response.json()


def test_private_club_roster_is_hidden_from_non_members(client):
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club(client, owner_headers, "Secret Club", is_public=False)

    _, outsider_headers = register(client, "outsider", "outsider@example.com")

    response = client.get(
        f"/clubs/{club['id']}/members",
        headers=outsider_headers,
    )

    assert response.status_code == 403


def test_private_club_roster_is_visible_to_members(client):
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club(client, owner_headers, "Secret Club", is_public=False)

    response = client.get(
        f"/clubs/{club['id']}/members",
        headers=owner_headers,
    )

    assert response.status_code == 200
    assert [member["username"] for member in response.json()] == ["owner"]


def test_public_club_roster_stays_browsable(client):
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club(client, owner_headers, "Open Club", is_public=True)

    _, reader_headers = register(client, "reader", "reader@example.com")

    response = client.get(
        f"/clubs/{club['id']}/members",
        headers=reader_headers,
    )

    assert response.status_code == 200


def test_roster_never_exposes_email_addresses(client):
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club(client, owner_headers, "Open Club", is_public=True)

    _, reader_headers = register(client, "reader", "reader@example.com")

    response = client.get(
        f"/clubs/{club['id']}/members",
        headers=reader_headers,
    )

    assert response.status_code == 200

    for member in response.json():
        assert "email" not in member
        assert "owner@example.com" not in str(member)


def test_roster_requires_authentication(client):
    _, owner_headers = register(client, "owner", "owner@example.com")
    club = make_club(client, owner_headers, "Open Club", is_public=True)

    response = client.get(f"/clubs/{club['id']}/members")

    assert response.status_code == 401


def test_roster_for_missing_club_returns_404(client):
    _, headers = register(client, "reader", "reader@example.com")

    response = client.get(
        "/clubs/999999/members",
        headers=headers,
    )

    assert response.status_code == 404
