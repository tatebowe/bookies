from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DashboardProfile(BaseModel):
    id: int
    username: str
    display_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardBook(BaseModel):
    id: int
    title: str
    authors: str | None = None

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
    rating: float | None = None
    review: str | None = None
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
    role: str
    active_cycle: DashboardCycle | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardHistoryItem(BaseModel):
    id: int
    status: str
    rating: float | None = None
    review: str | None = None
    book: DashboardBook
    club: DashboardClub

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardNote(BaseModel):
    id: int
    title: str | None = None
    content: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardResponse(BaseModel):
    profile: DashboardProfile

    current_readings: list[DashboardReading]

    clubs: list[DashboardMembership]

    history: list[DashboardHistoryItem]

    notes: list[DashboardNote]
