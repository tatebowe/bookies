def test_club_dashboard(client, auth_headers):

    club_response = client.post(
        "/clubs/",
        headers=auth_headers,
        json={
            "name": "Dashboard Club",
            "description": "Dashboard test",
            "is_public": True,
            "join_policy": "open",
        },
    )

    assert club_response.status_code == 200

    club_id = club_response.json()["id"]

    response = client.get(
        f"/clubs/{club_id}/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["club"]["id"] == club_id
    assert data["reading_progress"]["not_started"] == 0
    assert "members" in data


def test_club_dashboard_returns_member_role(
    client,
    auth_headers,
):

    club_response = client.post(
        "/clubs/",
        headers=auth_headers,
        json={
            "name": "Role Dashboard Club",
            "description": "Role test",
            "is_public": True,
            "join_policy": "open",
        },
    )

    club_id = club_response.json()["id"]

    response = client.get(
        f"/clubs/{club_id}/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["members"]) == 1

    assert data["members"][0]["role"] == "owner"
