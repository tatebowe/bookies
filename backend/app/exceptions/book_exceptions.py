class InvalidGoogleBooksIdError(Exception):
    """Raised when a Google Books volume ID is not a safe opaque token."""

    pass


class BookLookupUnavailableError(Exception):
    """Raised when Google Books cannot be reached or refuses the request.

    Upstream trouble is not our caller's fault, so it must not surface as an
    opaque 500 with a stack trace.
    """

    pass
