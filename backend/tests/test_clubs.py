def test_create_club(client, auth_headers):

    response = client.post(
        "/clubs/",
        headers=auth_headers,
        json={
            "name": "Test Book Club",
            "description": "A club for testing",
            "is_public": True,
            "join_policy": "open",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Book Club"
    assert data["description"] == "A club for testing"
