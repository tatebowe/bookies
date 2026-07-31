class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists."""

    pass


class UserNotFoundError(Exception):
    """Raised when a requested user cannot be found."""

    pass


class InvalidCredentialsError(Exception):
    """Raised when login credentials are incorrect."""

    pass


class UnverifiedEmailError(Exception):
    """Raised when an identity provider vouches for an unverified address."""

    pass
