"""Registration input constraints and profile lookup access."""

import pytest


def register(client, username, email, password="password123", display_name=None):
    payload = {
        "username": username,
        "email": email,
        "password": password,
    }

    if display_name is not None:
        payload["display_name"] = display_name

    return client.post("/users/", json=payload)


def auth_for(client, username, email, password="password123"):
    assert register(client, username, email, password).status_code == 200

    token = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    ).json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# --- Profile lookup requires a caller we can identify --------------------


def test_profile_lookup_requires_authentication(client):
    auth_for(client, "profileowner", "profileowner@example.com")

    response = client.get("/profiles/profileowner")

    assert response.status_code == 401


def test_profile_lookup_works_for_authenticated_readers(client):
    auth_for(client, "profileowner", "profileowner@example.com")
    headers = auth_for(client, "reader", "reader@example.com")

    response = client.get("/profiles/profileowner", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == "profileowner"


def test_profile_lookup_omits_notification_settings(client):
    """Those belong to the profile owner, not to whoever looks them up."""
    auth_for(client, "profileowner", "profileowner@example.com")
    headers = auth_for(client, "reader", "reader@example.com")

    body = client.get("/profiles/profileowner", headers=headers).json()

    assert "club_updates" not in body
    assert "cycle_reminders" not in body
    assert "reading_activity" not in body
    assert "email" not in body


# --- bcrypt truncation ---------------------------------------------------


def test_multibyte_password_over_72_bytes_is_rejected(client):
    """40 characters, 80 bytes. max_length alone would have let this through."""
    response = register(client, "multibyte", "mb@example.com", password="é" * 40)

    assert response.status_code == 422


def test_password_at_the_byte_limit_is_accepted(client):
    response = register(client, "atlimit", "atlimit@example.com", password="a" * 72)

    assert response.status_code == 200


def test_multibyte_password_within_the_byte_limit_is_accepted(client):
    response = register(client, "undermb", "undermb@example.com", password="é" * 36)

    assert response.status_code == 200


def test_short_password_still_rejected(client):
    response = register(client, "shortpw", "shortpw@example.com", password="abc")

    assert response.status_code == 422


# --- email and username ---------------------------------------------------


@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",
        "missing-at-sign.com",
        "two@@example.com",
        "trailing@",
        "",
    ],
)
def test_malformed_emails_are_rejected(client, email):
    response = register(client, "emailuser", email)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "username",
    [
        "ab",
        "a" * 33,
        "has space",
        "has/slash",
        "has@at",
        "",
    ],
)
def test_malformed_usernames_are_rejected(client, username):
    response = register(client, username, "userpattern@example.com")

    assert response.status_code == 422


def test_reasonable_username_is_accepted(client):
    response = register(client, "a_valid-Name9", "valid@example.com")

    assert response.status_code == 200
