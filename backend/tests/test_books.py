def test_create_book(client, auth_headers, mock_google_book):
    response = client.post(
        "/books/",
        headers=auth_headers,
        json={
            "google_books_id": "the-hobbit-test-id",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "The Hobbit"
    assert data["google_books_id"] == "the-hobbit-test-id"


def test_create_duplicate_book(client, auth_headers, mock_google_book):
    payload = {
        "google_books_id": "the-hobbit-test-id",
    }

    first = client.post(
        "/books/",
        headers=auth_headers,
        json=payload,
    )

    second = client.post(
        "/books/",
        headers=auth_headers,
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["id"] == second.json()["id"]


def test_create_book_requires_auth(client, mock_google_book):
    response = client.post(
        "/books/",
        json={
            "google_books_id": "the-hobbit-test-id",
        },
    )

    assert response.status_code == 401
