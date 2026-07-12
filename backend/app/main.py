from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import app.models
from app.database.database import Base, engine
from app.exceptions.club_exceptions import ClubAlreadyExistsError
from app.exceptions.club_reading_exceptions import (
    InvalidReadingStatusError,
)
from app.exceptions.cycle_phase_exceptions import (
    InvalidCyclePhaseError,
)
from app.exceptions.discussion_note_exceptions import (
    DiscussionNoteNotFoundError,
    UnauthorizedDiscussionNoteError,
)
from app.exceptions.join_request_exceptions import (
    InvalidJoinRequestError,
    JoinRequestAlreadyExistsError,
    JoinRequestNotFoundError,
)
from app.exceptions.permission_exceptions import (
    NotClubAdminError,
    NotClubOwnerError,
)
from app.exceptions.suggestion_exceptions import (
    NotClubMemberError,
    SuggestionAlreadyExistsError,
    SuggestionNotFoundError,
)
from app.exceptions.vote_exceptions import (
    AlreadyVotedError,
    VoteLimitExceededError,
)
from app.exceptions.voting_cycle_exceptions import (
    ActiveVotingCycleExistsError,
    InvalidVotingCycleError,
    VotingCycleNotFoundError,
    VotingTieError,
)
from app.routers import (
    auth,
    books,
    club_readings,
    clubs,
    discussion_notes,
    join_requests,
    suggestions,
    users,
    votes,
    voting_cycles,
)

# Create all database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bookies API",
    description="Backend API for managing book clubs",
    version="0.1.0",
)


# -------------------------
# Exception Handlers
# -------------------------


@app.exception_handler(VotingTieError)
def voting_tie_handler(
    request: Request,
    exc: VotingTieError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(SuggestionAlreadyExistsError)
def suggestion_exists_handler(
    request: Request,
    exc: SuggestionAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(InvalidCyclePhaseError)
def invalid_cycle_phase_handler(
    request: Request,
    exc: InvalidCyclePhaseError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(SuggestionNotFoundError)
def suggestion_not_found_handler(
    request: Request,
    exc: SuggestionNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(VotingCycleNotFoundError)
def voting_cycle_not_found_handler(
    request: Request,
    exc: VotingCycleNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(ActiveVotingCycleExistsError)
def active_cycle_exists_handler(
    request: Request,
    exc: ActiveVotingCycleExistsError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(InvalidVotingCycleError)
def invalid_cycle_handler(
    request: Request,
    exc: InvalidVotingCycleError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(AlreadyVotedError)
def already_voted_handler(
    request: Request,
    exc: AlreadyVotedError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(VoteLimitExceededError)
def vote_limit_handler(
    request: Request,
    exc: VoteLimitExceededError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(NotClubMemberError)
def not_club_member_handler(
    request: Request,
    exc: NotClubMemberError,
):
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(NotClubAdminError)
def not_club_admin_handler(
    request: Request,
    exc: NotClubAdminError,
):
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(NotClubOwnerError)
def not_club_owner_handler(
    request: Request,
    exc: NotClubOwnerError,
):
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(ClubAlreadyExistsError)
def club_already_exists_handler(
    request: Request,
    exc: ClubAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )


# -------------------------
# Health Routes
# -------------------------


@app.get("/")
def home():
    return {
        "message": "Welcome to Tome-Tet!",
        "status": "API is running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@app.exception_handler(JoinRequestAlreadyExistsError)
def join_request_exists_handler(
    request: Request,
    exc: JoinRequestAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(JoinRequestNotFoundError)
def join_request_not_found_handler(
    request: Request,
    exc: JoinRequestNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(InvalidJoinRequestError)
def invalid_join_request_handler(
    request: Request,
    exc: InvalidJoinRequestError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(InvalidReadingStatusError)
def invalid_reading_status_handler(
    request: Request,
    exc: InvalidReadingStatusError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(DiscussionNoteNotFoundError)
def discussion_note_not_found_handler(
    request: Request,
    exc: DiscussionNoteNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(UnauthorizedDiscussionNoteError)
def unauthorized_discussion_note_handler(
    request: Request,
    exc: UnauthorizedDiscussionNoteError,
):
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
        },
    )


# -------------------------
# API Routers
# -------------------------


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clubs.router)
app.include_router(books.router)
app.include_router(voting_cycles.router)
app.include_router(suggestions.router)
app.include_router(votes.router)
app.include_router(join_requests.router)
app.include_router(club_readings.router)
app.include_router(discussion_notes.router)
