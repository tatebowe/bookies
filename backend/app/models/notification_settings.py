from sqlalchemy import Boolean, Column, ForeignKey, Integer

from app.database.database import Base


class UserNotificationSettings(Base):
    __tablename__ = "user_notification_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    club_updates = Column(Boolean, default=True, nullable=False)
    cycle_reminders = Column(Boolean, default=True, nullable=False)
    reading_activity = Column(Boolean, default=True, nullable=False)
