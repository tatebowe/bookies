from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileResponse(BaseModel):
    id: int
    username: str
    display_name: str | None
    created_at: datetime
    club_updates: bool = True
    cycle_reminders: bool = True
    reading_activity: bool = True

    model_config = ConfigDict(
        from_attributes=True,
    )


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    club_updates: bool
    cycle_reminders: bool
    reading_activity: bool
