from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReadingNoteCreate(BaseModel):
    title: str | None = None
    content: str

    reading_entry_id: int | None = None
    club_reading_id: int | None = None


class ReadingNoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class ReadingNoteResponse(BaseModel):
    id: int

    user_id: int

    reading_entry_id: int | None
    club_reading_id: int | None

    title: str | None
    content: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
