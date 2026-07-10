class ClubNotFoundError(Exception):
    """Raised when a club cannot be found."""

    pass


class AlreadyMemberError(Exception):
    """Raised when a user is already a member of a club."""

    pass


class ClubAlreadyExistsError(Exception):
    """Raised when a club name already exists."""

    pass
