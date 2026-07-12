class JoinRequestAlreadyExistsError(Exception):
    """
    Raised when a user already has a pending join request.
    """

    pass


class JoinRequestNotFoundError(Exception):
    """
    Raised when a join request cannot be found.
    """

    pass


class InvalidJoinRequestError(Exception):
    """
    Raised when a join request cannot be processed.
    """

    pass
