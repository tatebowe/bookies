from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings


def verify_google_token(
    token: str,
) -> dict | None:
    """
    Verify a Google OAuth ID token.

    Returns:
        Google user information if valid.
        None if invalid.
    """

    try:
        google_user = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.google_client_id,
        )

        return google_user

    except ValueError:
        return None
