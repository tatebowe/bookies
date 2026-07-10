from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VoteCreate(BaseModel):
    suggestion_id: int


class VoteResponse(BaseModel):
    id: int

    suggestion_id: int
    user_id: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
