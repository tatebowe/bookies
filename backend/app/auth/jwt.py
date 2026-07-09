from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(data: dict):

    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_token(token: str):

    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )

    except JWTError:
        return None
