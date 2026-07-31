from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ClubCreate(BaseModel):
    name: str
    description: str | None = None
    is_public: bool = False

    max_votes_per_user: int = 1

    tie_break_method: Literal[
        "runoff",
        "owner_choice",
        "earliest_submission",
    ] = "runoff"

    join_policy: str = "request"


class ClubResponse(BaseModel):
    id: int
    name: str
    description: str | None

    is_public: bool

    max_votes_per_user: int

    tie_break_method: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

    join_policy: str


class ClubMemberResponse(BaseModel):
    # No email here. A member roster is visible to every reader who can see
    # the club, which is not an audience that should receive addresses.
    id: int
    username: str
    display_name: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClubSettingsUpdate(BaseModel):
    is_public: bool
    join_policy: str
    max_votes_per_user: int = Field(ge=1)


class ClubMemberRoleUpdate(BaseModel):
    role: Literal["member", "admin"]


class ClubDiscoveryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_public: bool
    join_policy: str
    member_count: int

    model_config = ConfigDict(
        from_attributes=True,
    )
