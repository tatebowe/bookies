from unittest.mock import patch


def test_google_login_creates_user(
    client,
):
    google_user = {
        "sub": "google-12345",
        "email": "googleuser@example.com",
        "name": "Google User",
    }

    with patch(
        "app.routers.auth.verify_google_token",
        return_value=google_user,
    ):
        response = client.post(
            "/auth/google",
            params={
                "token": "fake-google-token",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_google_login_existing_user(
    client,
):
    google_user = {
        "sub": "google-existing",
        "email": "existing@example.com",
        "name": "Existing User",
    }

    with patch(
        "app.routers.auth.verify_google_token",
        return_value=google_user,
    ):
        first_response = client.post(
            "/auth/google",
            params={
                "token": "fake-google-token",
            },
        )

        second_response = client.post(
            "/auth/google",
            params={
                "token": "fake-google-token",
            },
        )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_token = first_response.json()["access_token"]
    second_token = second_response.json()["access_token"]

    assert first_token == second_token


def test_google_login_invalid_token(
    client,
):
    with patch(
        "app.routers.auth.verify_google_token",
        return_value=None,
    ):
        response = client.post(
            "/auth/google",
            params={
                "token": "bad-token",
            },
        )

    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid Google token"
