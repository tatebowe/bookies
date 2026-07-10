class SuggestionNotFoundError(Exception):
    """Raised when a book suggestion cannot be found."""

    pass


class NotClubMemberError(Exception):
    """Raised when a user is not a member of the club."""

    pass


class SuggestionAlreadyExistsError(Exception):
    """Raised when a duplicate suggestion is created."""

    pass
