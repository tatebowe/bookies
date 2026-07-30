from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClubDashboardClub(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_public: bool
    join_policy: str
    max_votes_per_user: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClubDashboardBook(BaseModel):
    id: int
    title: str
    authors: str | None = None
    suggested_by_display_name: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardProgress(BaseModel):
    not_started: int
    reading: int
    completed: int


class DashboardMember(BaseModel):
    username: str
    display_name: str | None = None
    role: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class DashboardCycle(BaseModel):
    id: int
    name: str | None = None
    phase: str
    active: bool
    voting_end_date: datetime | None = None
    suggestion_start_date: datetime | None = None
    voting_start_date: datetime | None = None
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
    participation_cycle: DashboardCycle | None = None
    future_cycles: list[DashboardCycle] = []

    discussion_notes_count: int
    viewer_role: str
    viewer_club_reading_id: int | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )
