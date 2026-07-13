def test_empty_club_history(client, auth_headers):

    club_response = client.post(
        "/clubs/",
        headers=auth_headers,
        json={
            "name": "History Club",
            "description": "History test",
            "is_public": True,
            "join_policy": "open",
        },
    )

    club_id = club_response.json()["id"]

    response = client.get(
        f"/clubs/{club_id}/history",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["club_id"] == club_id
    assert data["history"] == []
