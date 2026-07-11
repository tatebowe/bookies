from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VotingCycleCreate(BaseModel):
    name: str | None = None
    start_date: datetime
    end_date: datetime


class VotingCycleResponse(BaseModel):
    id: int
    club_id: int
    name: str | None
    start_date: datetime
    end_date: datetime
    active: bool
    selected_book_id: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
