from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.exceptions.user_exceptions import UserAlreadyExistsError
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import register_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return register_user(db, user)

    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
