from sqlalchemy.orm import Session

from app.exceptions.user_exceptions import UserAlreadyExistsError
from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password, verify_password


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

    existing_username = db.query(User).filter(User.username == user.username).first()

    if existing_username:
        raise UserAlreadyExistsError("Username already exists")

    existing_email = db.query(User).filter(User.email == user.email).first()

    if existing_email:
        raise UserAlreadyExistsError("Email already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return db.get(User, user_id)


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    user = get_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


# Future user operations:
#
# - update_profile()
# - change_password()
# - request_password_reset()
# - delete_user()
# - deactivate_user()
