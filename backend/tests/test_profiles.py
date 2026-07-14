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

    response = client.get(
        "/profiles/profileuser",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "profileuser"
    assert data["display_name"] == "Profile User"
    assert "email" not in data


def test_profile_not_found(
    client,
):
    response = client.get(
        "/profiles/doesnotexist",
    )

    assert response.status_code == 404
