from app.integrations.google_books import search_books


def test_google_books():
    books = search_books("Mistborn")

    assert len(books) > 0
    assert books[0]["title"]
