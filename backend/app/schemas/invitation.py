from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvitationCreate(BaseModel):
    username: str


class InvitationResponse(BaseModel):
    """An invitation as the recipient sees it.

    Deliberately only the club's name. Someone who has not accepted yet is
    not a member, so they get nothing else about the club -- no description,
    roster, history or dashboard -- just enough to recognise the invitation.
    """

    id: int
    club_id: int
    club_name: str
    invited_by_username: str
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClubInvitationResponse(BaseModel):
    """An invitation as the sending club's admins see it."""

    id: int
    club_id: int
    invited_username: str
    invited_display_name: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
