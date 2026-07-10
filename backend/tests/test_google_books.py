from app.integrations.google_books import search_books


def test_google_books_search(mocker):
    mock_response = {
        "items": [
            {
                "id": "abc123",
                "volumeInfo": {
                    "title": "Mistborn: The Final Empire",
                    "authors": [
                        "Brandon Sanderson",
                    ],
                    "description": "A fantasy novel.",
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780765311788",
                        }
                    ],
                    "publishedDate": "2006",
                    "pageCount": 541,
                    "language": "en",
                    "categories": [
                        "Fantasy",
                    ],
                    "imageLinks": {
                        "thumbnail": "https://example.com/book.jpg",
                    },
                },
            }
        ]
    }

    mocker.patch(
        "httpx.get",
        return_value=mocker.Mock(
            json=lambda: mock_response,
            raise_for_status=lambda: None,
            status_code=200,
        ),
    )

    books = search_books(
        "Mistborn",
    )

    assert len(books) == 1

    book = books[0]

    assert book["google_books_id"] == "abc123"
    assert book["title"] == "Mistborn: The Final Empire"
    assert book["authors"] == "Brandon Sanderson"
    assert book["isbn"] == "9780765311788"
    assert book["page_count"] == 541
    assert book["language"] == "en"
