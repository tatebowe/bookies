import os
from unittest.mock import patch

import pytest
from app.database.database import Base
from app.dependencies import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(autouse=True)
def setup_database():
    if os.path.exists("test.db"):
        os.remove("test.db")

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

    engine.dispose()

    if os.path.exists("test.db"):
        os.remove("test.db")


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture
def mock_google_book():
    with patch("app.services.book_service.get_google_book_by_id") as mock:
        mock.return_value = {
            "google_books_id": "the-hobbit-test-id",
            "title": "The Hobbit",
            "authors": "J.R.R. Tolkien",
            "description": "A hobbit goes on an adventure.",
            "isbn": "9780261102217",
            "published_date": "1937",
            "page_count": 310,
            "language": "en",
            "categories": "Fantasy",
            "thumbnail_url": "https://example.com/hobbit.jpg",
        }

        yield mock


@pytest.fixture
def reading_entry(client, auth_headers, mock_google_book):
    book_response = client.post(
        "/books/",
        headers=auth_headers,
        json={
            "google_books_id": "the-hobbit-test-id",
        },
    )

    print(book_response.json())

    assert book_response.status_code == 200

    book = book_response.json()

    response = client.post(
        "/reading-entries/",
        headers=auth_headers,
        json={
            "book_id": book["id"],
            "status": "reading",
        },
    )

    assert response.status_code == 200

    return response.json()
