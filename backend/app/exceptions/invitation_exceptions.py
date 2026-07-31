class InvitationNotFoundError(Exception):
    """Raised when an invitation cannot be found."""

    pass


class InvitationAlreadyExistsError(Exception):
    """Raised when the user already has a pending invitation or membership."""

    pass


class InvalidInvitationError(Exception):
    """Raised when an invitation cannot be acted on as requested."""

    pass


class UnauthorizedInvitationError(Exception):
    """Raised when someone other than the recipient answers an invitation."""

    pass
