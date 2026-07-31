def auth_headers_for(client, username, email):
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


def test_get_profile_by_username(
    client,
):
    response = client.post(
        "/users/",
        json={
            "username": "profileuser",
            "email": "profile@example.com",
            "password": "password123",
            "display_name": "Profile User",
        },
    )

    assert response.status_code == 200

    headers = auth_headers_for(client, "viewer", "viewer@example.com")

    response = client.get(
        "/profiles/profileuser",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "profileuser"
    assert data["display_name"] == "Profile User"
    assert "email" not in data


def test_profile_not_found(
    client,
):
    headers = auth_headers_for(client, "viewer", "viewer@example.com")

    response = client.get(
        "/profiles/doesnotexist",
        headers=headers,
    )

    assert response.status_code == 404
