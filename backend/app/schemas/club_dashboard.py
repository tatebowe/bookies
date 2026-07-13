from pydantic import BaseModel


class DashboardClub(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class DashboardBook(BaseModel):
    id: int
    title: str
    authors: str | None = None

    class Config:
        from_attributes = True


class DashboardProgress(BaseModel):
    not_started: int
    reading: int
    completed: int


class DashboardMember(BaseModel):
    username: str
    status: str


class DashboardCycle(BaseModel):
    id: int
    phase: str

    class Config:
        from_attributes = True


class ClubDashboardResponse(BaseModel):
    club: DashboardClub
    current_book: DashboardBook | None = None
    reading_progress: DashboardProgress
    members: list[DashboardMember]
    active_cycle: DashboardCycle | None = None
    discussion_notes_count: int

    class Config:
        from_attributes = True
