# NotClubMemberError used to be declared here as well as in
# permission_exceptions. Two classes with one name meant the handler registered
# in main.py only ever matched one of them, so the membership checks in
# permission_service raised an exception nothing caught (a 500 instead of a
# 403). Re-export the permission_exceptions class so there is exactly one.
from app.exceptions.permission_exceptions import NotClubMemberError

__all__ = [
    "NotClubMemberError",
    "SuggestionAlreadyExistsError",
    "SuggestionNotFoundError",
]


class SuggestionAlreadyExistsError(Exception):
    pass


class SuggestionNotFoundError(Exception):
    pass
