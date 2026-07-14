from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VotingCycleCreate(BaseModel):
    name: str | None = None

    suggestion_start_date: datetime
    voting_start_date: datetime
    voting_end_date: datetime
    discussion_date: datetime


class VotingCycleResponse(BaseModel):
    id: int
    club_id: int
    name: str | None

    suggestion_start_date: datetime
    voting_start_date: datetime
    voting_end_date: datetime
    discussion_date: datetime

    active: bool
    phase: str

    selected_book_id: int | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
