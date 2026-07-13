from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryBook(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    title: str
    authors: str | None


class CycleHistoryItem(BaseModel):
    cycle_id: int
    book: HistoryBook

    start_date: datetime
    end_date: datetime

    members_started: int
    members_completed: int


class ClubHistoryResponse(BaseModel):
    club_id: int
    club_name: str

    history: list[CycleHistoryItem]
