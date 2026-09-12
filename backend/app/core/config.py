from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60

    google_books_api_key: str | None = None
    google_client_id: str | None = None

    # Shared invite code required to create an account. Unset means signup is
    # open, which is the convenient default for local development and tests.
    signup_code: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
