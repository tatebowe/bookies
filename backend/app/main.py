from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import app.models
from app.database.database import Base, engine
from app.exceptions.suggestion_exceptions import (
    SuggestionAlreadyExistsError,
    SuggestionNotFoundError,
)
from app.exceptions.voting_cycle_exceptions import (
    VotingCycleNotFoundError,
    VotingTieError,
)
from app.routers import (
    auth,
    books,
    clubs,
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


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clubs.router)
app.include_router(books.router)
app.include_router(voting_cycles.router)
app.include_router(suggestions.router)
app.include_router(votes.router)
