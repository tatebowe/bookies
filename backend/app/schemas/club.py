from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


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


class ClubMemberResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(
        from_attributes=True,
    )
