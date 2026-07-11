from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClubCreate(BaseModel):
    name: str
    description: str | None = None
    is_public: bool = False


class ClubResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_public: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClubMemberResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    username: str
    email: str
