from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.google import verify_google_token
from app.auth.jwt import create_access_token
from app.dependencies import get_db
from app.schemas.auth import TokenResponse
from app.services.user_service import (
    authenticate_user,
    get_or_create_google_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "sub": str(user.id),
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post(
    "/google",
    response_model=TokenResponse,
)
def google_login(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Authenticate using a Google OAuth ID token.
    """

    google_user = verify_google_token(
        token,
    )

    if google_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    user = get_or_create_google_user(
        db,
        google_user,
    )

    access_token = create_access_token(
        {
            "sub": str(user.id),
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
