from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.exceptions.suggestion_exceptions import (
    NotClubMemberError,
    SuggestionAlreadyExistsError,
    SuggestionNotFoundError,
)
from app.models.user import User
from app.schemas.suggestion import (
    BookSuggestionCreate,
    BookSuggestionResponse,
)
from app.services.suggestion_service import (
    create_suggestion,
    get_club_suggestions,
)

router = APIRouter(
    prefix="/clubs",
    tags=["Suggestions"],
)


@router.post(
    "/{club_id}/suggestions",
    response_model=BookSuggestionResponse,
)
def suggest_book(
    club_id: int,
    suggestion: BookSuggestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_suggestion(
            db,
            club_id,
            suggestion.book_id,
            current_user.id,
            suggestion.anonymous,
        )

    except NotClubMemberError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except SuggestionAlreadyExistsError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except SuggestionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/{club_id}/suggestions",
    response_model=list[BookSuggestionResponse],
)
def list_suggestions(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get suggestions for the current voting cycle.
    """

    return get_club_suggestions(
        db,
        club_id,
    )
