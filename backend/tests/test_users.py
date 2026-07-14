def test_create_user_with_display_name(client):
    response = client.post(
        "/users/",
        json={
            "username": "displayuser",
            "email": "display@example.com",
            "password": "password123",
            "display_name": "Display User",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "displayuser"
    assert data["email"] == "display@example.com"
    assert data["display_name"] == "Display User"


def test_create_user_without_display_name(client):
    response = client.post(
        "/users/",
        json={
            "username": "nodisplay",
            "email": "nodisplay@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "nodisplay"
    assert data["display_name"] is None


def test_cannot_create_duplicate_username(client):
    first = client.post(
        "/users/",
        json={
            "username": "duplicateuser",
            "email": "first@example.com",
            "password": "password123",
            "display_name": "First User",
        },
    )

    second = client.post(
        "/users/",
        json={
            "username": "duplicateuser",
            "email": "second@example.com",
            "password": "password123",
            "display_name": "Second User",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 400


def test_user_response_does_not_require_display_name(client):
    response = client.post(
        "/users/",
        json={
            "username": "optionaldisplay",
            "email": "optional@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "display_name" in data
    assert data["display_name"] is None
