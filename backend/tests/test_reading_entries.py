def test_create_reading_entry(client, auth_headers, mock_google_book):

    book_response = client.post(
        "/books/",
        headers=auth_headers,
        json={
            "google_books_id": "the-hobbit-test-id",
        },
    )

    book = book_response.json()

    response = client.post(
        "/reading-entries/",
        headers=auth_headers,
        json={
            "book_id": book["id"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["book_id"] == book["id"]
    assert data["status"] == "not_started"


def test_create_reading_entry_requires_auth(client):
    response = client.post(
        "/reading-entries/",
        json={
            "book_id": 1,
            "status": "reading",
        },
    )

    assert response.status_code == 401


def test_cannot_update_someone_elses_reading_entry(
    client,
    auth_headers,
    reading_entry,
):
    # create second user
    response = client.post(
        "/users/",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    login = client.post(
        "/auth/login",
        data={
            "username": "second@example.com",
            "password": "password123",
        },
    )

    second_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.patch(
        f"/reading-entries/{reading_entry['id']}/status",
        headers=second_headers,
        json={
            "status": "completed",
        },
    )

    assert response.status_code in [403, 404]


def test_update_reading_status(
    client,
    auth_headers,
    reading_entry,
):

    response = client.patch(
        f"/reading-entries/{reading_entry['id']}/status",
        headers=auth_headers,
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_invalid_reading_status(
    client,
    auth_headers,
    reading_entry,
):
    response = client.patch(
        f"/reading-entries/{reading_entry['id']}/status",
        headers=auth_headers,
        json={
            "status": "banana",
        },
    )

    assert response.status_code == 400


def test_cannot_create_duplicate_reading_entry(
    client,
    auth_headers,
    reading_entry,
):
    response = client.post(
        "/reading-entries/",
        headers=auth_headers,
        json={
            "book_id": reading_entry["book_id"],
            "status": "reading",
        },
    )

    assert response.status_code in [400, 409]


# TODO: add delete endpoint and test later
# def test_delete_reading_entry(
#     client,
#     auth_headers,
#     reading_entry,
# ):

#     response = client.delete(
#         f"/reading-entries/{reading_entry['id']}",
#         headers=auth_headers,
#     )

#     assert response.status_code == 200
