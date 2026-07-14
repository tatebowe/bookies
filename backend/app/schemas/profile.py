from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileResponse(BaseModel):
    id: int
    username: str
    display_name: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
