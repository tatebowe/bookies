class AlreadyVotedError(Exception):
    """Raised when a user votes on the same suggestion twice."""

    pass


class VoteLimitExceededError(Exception):
    """Raised when a user exceeds their allowed votes."""

    pass


class VoteNotFoundError(Exception):
    """Raised when a vote cannot be found."""

    pass
