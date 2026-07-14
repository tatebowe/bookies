from datetime import datetime, timedelta, timezone


def create_test_club(
    client,
    auth_headers,
):
    response = client.post(
        "/clubs/",
        headers=auth_headers,
        json={
            "name": "Voting Test Club",
            "description": "Testing voting cycles",
        },
    )

    assert response.status_code == 200

    return response.json()


def test_create_voting_cycle(
    client,
    auth_headers,
):
    club = create_test_club(
        client,
        auth_headers,
    )

    now = datetime.now(timezone.utc)

    response = client.post(
        f"/clubs/{club['id']}/cycles",
        headers=auth_headers,
        json={
            "name": "July Reading Cycle",
            "suggestion_start_date": (now + timedelta(hours=1)).isoformat(),
            "voting_start_date": (now + timedelta(days=2)).isoformat(),
            "voting_end_date": (now + timedelta(days=5)).isoformat(),
            "discussion_date": (now + timedelta(days=12)).isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "July Reading Cycle"
    assert data["phase"] == "suggestion"
    assert data["active"] is True


def test_get_active_cycle(
    client,
    auth_headers,
):
    club = create_test_club(
        client,
        auth_headers,
    )

    now = datetime.now(timezone.utc)

    create_response = client.post(
        f"/clubs/{club['id']}/cycles",
        headers=auth_headers,
        json={
            "suggestion_start_date": now.isoformat(),
            "voting_start_date": (now + timedelta(days=2)).isoformat(),
            "voting_end_date": (now + timedelta(days=5)).isoformat(),
            "discussion_date": (now + timedelta(days=12)).isoformat(),
        },
    )

    assert create_response.status_code == 200

    response = client.get(
        f"/clubs/{club['id']}/cycles/active",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["phase"] == "suggestion"
    assert data["active"] is True


def test_create_cycle_invalid_dates(
    client,
    auth_headers,
):
    club = create_test_club(
        client,
        auth_headers,
    )

    now = datetime.now(timezone.utc)

    response = client.post(
        f"/clubs/{club['id']}/cycles",
        headers=auth_headers,
        json={
            "suggestion_start_date": (now + timedelta(days=5)).isoformat(),
            "voting_start_date": (now + timedelta(days=2)).isoformat(),
            "voting_end_date": (now + timedelta(days=1)).isoformat(),
            "discussion_date": (now + timedelta(days=10)).isoformat(),
        },
    )

    assert response.status_code in [400, 422]


def test_cannot_create_multiple_active_cycles(
    client,
    auth_headers,
):
    club = create_test_club(
        client,
        auth_headers,
    )

    now = datetime.now(timezone.utc)

    payload = {
        "suggestion_start_date": (now).isoformat(),
        "voting_start_date": (now + timedelta(days=2)).isoformat(),
        "voting_end_date": (now + timedelta(days=5)).isoformat(),
        "discussion_date": (now + timedelta(days=12)).isoformat(),
    }

    first = client.post(
        f"/clubs/{club['id']}/cycles",
        headers=auth_headers,
        json=payload,
    )

    second = client.post(
        f"/clubs/{club['id']}/cycles",
        headers=auth_headers,
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code in [400, 409]
