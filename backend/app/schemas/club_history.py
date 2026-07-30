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
    cycle_name: str | None = None
    book: HistoryBook

    start_date: datetime
    end_date: datetime

    members_started: int
    members_completed: int
    discussion_notes_count: int = 0


class ClubHistoryResponse(BaseModel):
    club_id: int
    club_name: str

    history: list[CycleHistoryItem]
