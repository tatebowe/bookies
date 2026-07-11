class NotClubMemberError(Exception):
    """Raised when a user is not a member of the club."""

    pass


class SuggestionAlreadyExistsError(Exception):
    """Raised when a duplicate suggestion is created."""

    pass


class NoActiveVotingCycleError(Exception):
    """Raised when a club has no active voting cycle."""

    pass
