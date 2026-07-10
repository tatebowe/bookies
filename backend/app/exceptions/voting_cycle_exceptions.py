class VotingCycleNotFoundError(Exception):
    """Raised when a voting cycle cannot be found."""

    pass


class ActiveVotingCycleExistsError(Exception):
    """Raised when attempting to create multiple active cycles."""

    pass


class InvalidVotingCycleError(Exception):
    """Raised when a voting cycle date range is invalid."""

    pass
