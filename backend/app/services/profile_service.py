from sqlalchemy.orm import Session

from app.exceptions.user_exceptions import UserNotFoundError
from app.models.user import User


def get_profile_by_username(
    db: Session,
    username: str,
) -> User:

    user = (
        db.query(User)
        .filter(
            User.username == username,
        )
        .first()
    )

    if user is None:
        raise UserNotFoundError("User not found")

    return user
