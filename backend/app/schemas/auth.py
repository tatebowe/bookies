from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class GoogleLoginRequest(BaseModel):
    # Carried in the body, never the query string: a Google ID token is a
    # credential, and query strings land in access logs, proxy logs, Referer
    # headers and browser history.
    token: str
    # Only consulted when the token belongs to someone without an account yet.
    signup_code: str | None = None
