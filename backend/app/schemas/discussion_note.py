from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DiscussionNoteCreate(BaseModel):
    title: str | None = None
    content: str


class DiscussionNoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class DiscussionNoteResponse(BaseModel):
    id: int

    club_reading_id: int

    title: str | None
    content: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
