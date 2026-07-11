from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.exceptions.suggestion_exceptions import NotClubMemberError
from app.exceptions.vote_exceptions import (
    AlreadyVotedError,
    VoteLimitExceededError,
)
from app.models.user import User
from app.schemas.vote import VoteResponse
from app.services.voting_service import (
    cast_vote,
    remove_vote,
)

router = APIRouter(
    prefix="/suggestions",
    tags=["Votes"],
)


@router.post(
    "/{suggestion_id}/vote",
    response_model=VoteResponse,
)
def vote_for_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Vote for a book suggestion.
    """

    try:
        return cast_vote(
            db,
            suggestion_id,
            current_user.id,
        )

    except NotClubMemberError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except AlreadyVotedError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except VoteLimitExceededError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.delete(
    "/{suggestion_id}/vote",
)
def remove_vote_from_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove the current user's vote.
    """

    try:
        remove_vote(
            db,
            suggestion_id,
            current_user.id,
        )

        return {
            "message": "Vote removed",
            "suggestion_id": suggestion_id,
        }

    except AlreadyVotedError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
