from pydantic import BaseModel, ConfigDict


class MembershipResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    club_id: int
    role: str
