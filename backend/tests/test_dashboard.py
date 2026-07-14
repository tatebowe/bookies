def test_user_dashboard_empty(
    client,
    auth_headers,
):

    response = client.get(
        "/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "clubs" in data
    assert data["clubs"] == []
