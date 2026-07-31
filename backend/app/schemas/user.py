from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

BCRYPT_MAX_PASSWORD_BYTES = 72

USERNAME_PATTERN = r"^[A-Za-z0-9_-]+$"


class UserCreate(BaseModel):
    username: str = Field(
        pattern=USERNAME_PATTERN,
        min_length=3,
        max_length=32,
    )
    email: EmailStr
    password: str = Field(min_length=8, max_length=BCRYPT_MAX_PASSWORD_BYTES)
    display_name: str | None = Field(default=None, max_length=64)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        # max_length counts characters; bcrypt's limit is bytes. "é" * 40 is
        # 40 characters but 80 bytes, and would be truncated on the way in.
        if len(value.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(
                "Password must be at most "
                f"{BCRYPT_MAX_PASSWORD_BYTES} bytes when UTF-8 encoded"
            )

        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    username: str
    display_name: str | None
    email: str
