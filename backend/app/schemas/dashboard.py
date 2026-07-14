from pydantic import BaseModel, ConfigDict


class DashboardClub(BaseModel):

    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardReading(BaseModel):

    status: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardCycle(BaseModel):

    id: int
    phase: str
    active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserDashboardClub(BaseModel):

    club: DashboardClub
    active_cycle: DashboardCycle | None = None
    current_reading: DashboardReading | None = None


class DashboardResponse(BaseModel):

    clubs: list[UserDashboardClub]
