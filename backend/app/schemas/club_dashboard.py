from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClubDashboardClub(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClubDashboardBook(BaseModel):
    id: int
    title: str
    authors: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardProgress(BaseModel):
    not_started: int
    reading: int
    completed: int


class DashboardMember(BaseModel):
    username: str
    role: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardCycle(BaseModel):
    id: int
    phase: str
    active: bool
    voting_end_date: datetime | None = None
    discussion_date: datetime | None = None
    selected_book: ClubDashboardBook | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClubDashboardResponse(BaseModel):
    club: ClubDashboardClub

    current_book: ClubDashboardBook | None = None

    reading_progress: DashboardProgress

    members: list[DashboardMember]

    active_cycle: DashboardCycle | None = None

    discussion_notes_count: int

    model_config = ConfigDict(
        from_attributes=True,
    )
