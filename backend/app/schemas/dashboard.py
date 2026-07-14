from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DashboardBook(BaseModel):
    id: int
    title: str
    author: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardClub(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardReading(BaseModel):
    id: int
    status: str
    book: DashboardBook
    club: DashboardClub

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardCycle(BaseModel):
    id: int
    phase: str
    active: bool
    voting_end_date: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardMembership(BaseModel):
    club: DashboardClub
    active_cycle: DashboardCycle | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardHistoryItem(BaseModel):
    id: int
    book: DashboardBook
    club: DashboardClub
    status: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardResponse(BaseModel):

    current_readings: list[DashboardReading]

    clubs: list[DashboardMembership]

    history: list[DashboardHistoryItem]
