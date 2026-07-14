from sqlalchemy.orm import Session

from app.exceptions.user_exceptions import UserAlreadyExistsError
from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password, verify_password
from app.services.helpers import exists, get_by_id, save_and_refresh


def register_user(
    db: Session,
    user: UserCreate,
) -> User:
    """
    Create a new user.

    Raises:
        UserAlreadyExistsError:
            If the username or email already exists.
    """

    if exists(
        db,
        User,
        username=user.username,
    ):
        raise UserAlreadyExistsError("Username already exists")

    if exists(
        db,
        User,
        email=user.email,
    ):
        raise UserAlreadyExistsError("Email already exists")

    new_user = User(
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        password_hash=hash_password(user.password),
    )

    return save_and_refresh(
        db,
        new_user,
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return (
        db.query(User)
        .filter(
            User.email == email,
        )
        .first()
    )


def get_user_by_google_id(
    db: Session,
    google_id: str,
) -> User | None:
    """
    Retrieve a user by Google OAuth ID.
    """

    return (
        db.query(User)
        .filter(
            User.google_id == google_id,
        )
        .first()
    )


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return get_by_id(
        db,
        User,
        user_id,
    )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        return None

    if user.password_hash is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def create_google_user(
    db: Session,
    google_id: str,
    email: str,
    display_name: str | None,
) -> User:
    """
    Create a user from Google OAuth information.
    """

    existing_email = get_user_by_email(
        db,
        email,
    )

    if existing_email:
        raise UserAlreadyExistsError("A user with this email already exists")

    new_user = User(
        username=email.split("@")[0],
        display_name=display_name,
        email=email,
        google_id=google_id,
        password_hash=None,
    )

    return save_and_refresh(
        db,
        new_user,
    )


def get_or_create_google_user(
    db: Session,
    google_user: dict,
) -> User:
    """
    Find an existing Google user or create one.
    """

    google_id = google_user["sub"]
    email = google_user["email"]
    display_name = google_user.get("name")

    user = get_user_by_google_id(
        db,
        google_id,
    )

    if user:
        return user

    return create_google_user(
        db,
        google_id,
        email,
        display_name,
    )
