def test_login_returns_token(client):
    client.post(
        "/users/",
        json={
            "username": "loginuser",
            "email": "login@test.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login@test.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_me_requires_auth(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_get_me_with_auth(client, auth_headers):
    response = client.get(
        "/users/me",
        headers=auth_headers,
    )
    assert response.status_code == 200

    assert response.json()["username"] == "testuser"
