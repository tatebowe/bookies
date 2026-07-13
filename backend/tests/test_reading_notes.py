def test_create_reading_note(client, auth_headers, reading_entry):

    response = client.post(
        "/reading-notes/",
        headers=auth_headers,
        json={
            "title": "Chapter 1",
            "content": "Interesting opening chapter",
            "reading_entry_id": reading_entry["id"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "Interesting opening chapter"
    assert data["reading_entry_id"] == reading_entry["id"]


def test_get_my_reading_notes(client, auth_headers, reading_entry):

    client.post(
        "/reading-notes/",
        headers=auth_headers,
        json={
            "title": "Note",
            "content": "Thoughts",
            "reading_entry_id": reading_entry["id"],
        },
    )

    response = client.get(
        "/reading-notes/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["content"] == "Thoughts"


def test_update_reading_note(client, auth_headers, reading_entry):

    create = client.post(
        "/reading-notes/",
        headers=auth_headers,
        json={
            "title": "Old title",
            "content": "Old content",
            "reading_entry_id": reading_entry["id"],
        },
    )

    note_id = create.json()["id"]

    response = client.patch(
        f"/reading-notes/{note_id}",
        headers=auth_headers,
        json={
            "title": "New title",
            "content": "Updated content",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New title"
    assert data["content"] == "Updated content"


def test_delete_reading_note(client, auth_headers, reading_entry):

    create = client.post(
        "/reading-notes/",
        headers=auth_headers,
        json={
            "content": "Delete me",
            "reading_entry_id": reading_entry["id"],
        },
    )

    note_id = create.json()["id"]

    response = client.delete(
        f"/reading-notes/{note_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_cannot_update_someone_elses_note(
    client,
    auth_headers,
    reading_entry,
):
    create = client.post(
        "/reading-notes/",
        headers=auth_headers,
        json={
            "content": "Private note",
            "reading_entry_id": reading_entry["id"],
        },
    )

    note_id = create.json()["id"]

    client.post(
        "/users/",
        json={
            "username": "seconduser",
            "email": "second@test.com",
            "password": "password123",
        },
    )

    login = client.post(
        "/auth/login",
        data={
            "username": "second@test.com",
            "password": "password123",
        },
    )

    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.patch(
        f"/reading-notes/{note_id}",
        headers=headers,
        json={
            "content": "Trying to edit",
        },
    )

    assert response.status_code == 403
