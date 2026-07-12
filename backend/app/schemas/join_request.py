from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JoinRequestResponse(BaseModel):
    id: int

    club_id: int
    user_id: int

    status: str

    created_at: datetime

    reviewed_at: datetime | None
    reviewed_by_user_id: int | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class JoinRequestDecision(BaseModel):
    approved: bool
