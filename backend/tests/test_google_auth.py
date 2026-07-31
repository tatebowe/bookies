from unittest.mock import patch


def test_google_login_creates_user(
    client,
):
    google_user = {
        "sub": "google-12345",
        "email": "googleuser@example.com",
        "email_verified": True,
        "name": "Google User",
    }

    with patch(
        "app.routers.auth.verify_google_token",
        return_value=google_user,
    ):
        response = client.post(
            "/auth/google",
            json={
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
        "email_verified": True,
        "name": "Existing User",
    }

    with patch(
        "app.routers.auth.verify_google_token",
        return_value=google_user,
    ):
        first_response = client.post(
            "/auth/google",
            json={
                "token": "fake-google-token",
            },
        )

        second_response = client.post(
            "/auth/google",
            json={
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
            json={
                "token": "bad-token",
            },
        )

    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid Google token"


def test_google_token_is_not_accepted_from_the_query_string(client):
    """A credential in the URL ends up in logs, Referer headers and history."""
    google_user = {
        "sub": "google-query",
        "email": "query@example.com",
        "email_verified": True,
        "name": "Query User",
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

    assert response.status_code == 422


def test_google_token_is_declared_as_a_body_parameter(client):
    schema = client.get("/openapi.json").json()

    operation = schema["paths"]["/auth/google"]["post"]

    assert "parameters" not in operation
    assert "requestBody" in operation


def google_signin(client, google_user):
    with patch(
        "app.routers.auth.verify_google_token",
        return_value=google_user,
    ):
        return client.post(
            "/auth/google",
            json={
                "token": "fake-google-token",
            },
        )


def test_unverified_google_email_is_rejected(client):
    """Without email_verified, the address is only a claim, not a fact."""
    response = google_signin(
        client,
        {
            "sub": "google-unverified",
            "email": "victim@example.com",
            "email_verified": False,
            "name": "Unverified User",
        },
    )

    assert response.status_code == 403


def test_missing_email_verified_claim_is_rejected(client):
    response = google_signin(
        client,
        {
            "sub": "google-no-claim",
            "email": "victim@example.com",
            "name": "No Claim User",
        },
    )

    assert response.status_code == 403


def test_missing_email_is_rejected(client):
    response = google_signin(
        client,
        {
            "sub": "google-no-email",
            "email_verified": True,
            "name": "No Email User",
        },
    )

    assert response.status_code == 403


def test_string_true_email_verified_claim_is_accepted(client):
    """Google issues this claim as a bool or the string "true"."""
    response = google_signin(
        client,
        {
            "sub": "google-string-claim",
            "email": "stringclaim@example.com",
            "email_verified": "true",
            "name": "String Claim User",
        },
    )

    assert response.status_code == 200


def test_unverified_email_creates_no_account(client):
    google_signin(
        client,
        {
            "sub": "google-unverified",
            "email": "victim@example.com",
            "email_verified": False,
            "name": "Unverified User",
        },
    )

    login = client.post(
        "/auth/login",
        data={
            "username": "victim@example.com",
            "password": "password123",
        },
    )

    assert login.status_code == 401
