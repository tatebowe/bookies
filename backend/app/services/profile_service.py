from sqlalchemy.orm import Session

from app.exceptions.user_exceptions import UserNotFoundError
from app.models.notification_settings import UserNotificationSettings
from app.models.user import User
from app.services.name_moderation_service import ensure_allowed_name


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


def get_profile_settings(db: Session, user: User) -> dict:
    settings = (
        db.query(UserNotificationSettings)
        .filter(UserNotificationSettings.user_id == user.id)
        .first()
    )
    if settings is None:
        settings = UserNotificationSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "created_at": user.created_at,
        "club_updates": settings.club_updates,
        "cycle_reminders": settings.cycle_reminders,
        "reading_activity": settings.reading_activity,
    }


def update_profile_settings(
    db: Session,
    user: User,
    display_name: str | None,
    club_updates: bool,
    cycle_reminders: bool,
    reading_activity: bool,
) -> dict:
    if display_name:
        ensure_allowed_name(display_name, "display name")
    user.display_name = display_name.strip() if display_name else None
    settings = (
        db.query(UserNotificationSettings)
        .filter(UserNotificationSettings.user_id == user.id)
        .first()
    )
    if settings is None:
        settings = UserNotificationSettings(user_id=user.id)
        db.add(settings)
    settings.club_updates = club_updates
    settings.cycle_reminders = cycle_reminders
    settings.reading_activity = reading_activity
    db.commit()
    db.refresh(user)
    db.refresh(settings)
    return get_profile_settings(db, user)
