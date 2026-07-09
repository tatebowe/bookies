from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.security import hash_password
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
