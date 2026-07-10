from datetime import datetime

from pydantic import BaseModel


class ClubCreate(BaseModel):
    name: str
    description: str | None = None


class ClubResponse(BaseModel):

    id: int
    name: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True
