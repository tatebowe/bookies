import secrets

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.exceptions.signup_exceptions import InvalidSignupCodeError
from app.exceptions.user_exceptions import (
    UnverifiedEmailError,
    UserAlreadyExistsError,
)
from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password, verify_password
from app.services.helpers import exists, get_by_id, save_and_refresh
from app.services.name_moderation_service import ensure_allowed_name


def ensure_signup_allowed(
    signup_code: str | None,
) -> None:
    """
    Gate account creation behind a shared invite code.

    Every path that creates an account funnels through here, so a new one is
    only unguarded if it also skips this check. No configured code means
    signup is open.

    Raises:
        InvalidSignupCodeError:
            If a code is configured and the supplied one does not match.
    """

    expected = settings.signup_code

    if not expected:
        return

    # compare_digest rather than ==: the comparison is against a shared secret,
    # and it also handles the None case without a separate branch.
    if signup_code is None or not secrets.compare_digest(
        signup_code,
        expected,
    ):
        raise InvalidSignupCodeError(
            "A valid signup code is required to create an account",
        )


def register_user(
    db: Session,
    user: UserCreate,
) -> User:
    """
    Create a new user.

    Raises:
        UserAlreadyExistsError:
            If the username or email already exists.
        InvalidSignupCodeError:
            If a signup code is configured and the supplied one is wrong.
    """

    ensure_signup_allowed(user.signup_code)

    ensure_allowed_name(user.username, "username")
    if user.display_name:
        ensure_allowed_name(user.display_name, "display name")

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


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:
    return (
        db.query(User)
        .filter(
            User.username == username,
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
    identifier: str,
    password: str,
) -> User | None:

    user = (
        db.query(User)
        .filter(
            or_(
                User.email == identifier,
                User.username == identifier,
            )
        )
        .first()
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

    username = email.split("@")[0]
    ensure_allowed_name(username, "username")
    if display_name:
        ensure_allowed_name(display_name, "display name")

    existing_email = get_user_by_email(
        db,
        email,
    )

    if existing_email:
        raise UserAlreadyExistsError("A user with this email already exists")

    new_user = User(
        username=username,
        display_name=display_name,
        email=email,
        google_id=google_id,
        password_hash=None,
    )

    return save_and_refresh(
        db,
        new_user,
    )


def is_verified_email(google_user: dict) -> bool:
    """
    Read Google's email_verified claim, which arrives as either a bool or
    the string "true" depending on how the token was issued.
    """

    claim = google_user.get("email_verified")

    if isinstance(claim, str):
        return claim.strip().lower() == "true"

    return claim is True


def get_or_create_google_user(
    db: Session,
    google_user: dict,
    signup_code: str | None = None,
) -> User:
    """
    Find an existing Google user or create one.

    Raises:
        UnverifiedEmailError:
            If Google has not verified the address. Acting on an unverified
            address would let someone claim an address they do not control.
        InvalidSignupCodeError:
            If creating a new account and the signup code is wrong. Existing
            users are unaffected: the gate gets checked on creation only, so
            it never locks out anyone who already has an account.
    """

    google_id = google_user["sub"]
    email = google_user.get("email")
    display_name = google_user.get("name")

    if not email or not is_verified_email(google_user):
        raise UnverifiedEmailError(
            "Google account email is missing or unverified",
        )

    user = get_user_by_google_id(
        db,
        google_id,
    )

    if user:
        return user

    ensure_signup_allowed(signup_code)

    return create_google_user(
        db,
        google_id,
        email,
        display_name,
    )
