from unittest.mock import patch

import pytest
from app.core.config import settings

SIGNUP_CODE = "let-me-in-please"


@pytest.fixture
def signup_code(monkeypatch):
    monkeypatch.setattr(settings, "signup_code", SIGNUP_CODE)

    return SIGNUP_CODE


def register(client, **overrides):
    payload = {
        "username": "newreader",
        "email": "newreader@example.com",
        "password": "password123",
    }
    payload.update(overrides)

    return client.post("/users/", json=payload)


def test_signup_open_when_no_code_configured(client):
    # settings.signup_code defaults to None, so the gate stays out of the way
    # for local development and the rest of the suite.
    assert register(client).status_code == 200


def test_signup_rejected_when_code_omitted(client, signup_code):
    response = register(client)

    assert response.status_code == 403
    assert "signup code" in response.json()["detail"].lower()


def test_signup_rejected_with_wrong_code(client, signup_code):
    assert register(client, signup_code="guessing").status_code == 403


def test_signup_rejected_with_code_prefix(client, signup_code):
    # A prefix of the real code must not pass: compare_digest is length-aware.
    assert register(client, signup_code=SIGNUP_CODE[:-1]).status_code == 403


def test_signup_allowed_with_correct_code(client, signup_code):
    response = register(client, signup_code=SIGNUP_CODE)

    assert response.status_code == 200
    assert response.json()["username"] == "newreader"
    # The code must never come back out in the response body.
    assert "signup_code" not in response.json()


def google_login(client, sub, **extra):
    google_user = {
        "sub": sub,
        "email": f"{sub}@example.com",
        "email_verified": True,
        "name": "Google Reader",
    }

    with patch(
        "app.routers.auth.verify_google_token",
        return_value=google_user,
    ):
        return client.post(
            "/auth/google",
            json={"token": "fake-google-token", **extra},
        )


def test_google_signup_rejected_without_code(client, signup_code):
    # Google sign-in creates accounts too, so gating only /users/ would leave
    # signup open to anyone with a Google account.
    response = google_login(client, "google-newcomer")

    assert response.status_code == 403


def test_google_signup_allowed_with_correct_code(client, signup_code):
    response = google_login(
        client,
        "google-invited",
        signup_code=SIGNUP_CODE,
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_google_login_of_existing_user_needs_no_code(client, signup_code):
    assert (
        google_login(
            client,
            "google-regular",
            signup_code=SIGNUP_CODE,
        ).status_code
        == 200
    )

    # Signing in again is not signing up: the gate is checked on creation only,
    # so turning it on must not lock out people who already have accounts.
    assert google_login(client, "google-regular").status_code == 200
