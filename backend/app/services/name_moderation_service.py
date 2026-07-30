import re
import unicodedata

from app.exceptions.moderation_exceptions import NameNotAllowedError

# Keep this intentionally small and easy to expand as Tomeys' moderation policy evolves.
BLOCKED_NAME_TERMS = frozenset(
    {
        "bitch",
        "cunt",
        "faggot",
        "fuck",
        "nigger",
        "shit",
        "slut",
        "whore",
    }
)


def ensure_allowed_name(value: str, label: str) -> None:
    """Reject an obvious blocked term in a username or club name."""
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    )
    normalized = normalized.translate(
        str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"})
    )
    tokens = re.findall(r"[a-z0-9]+", normalized)

    for token in tokens:
        if any(
            re.fullmatch(rf"{re.escape(term)}\d*", token) for term in BLOCKED_NAME_TERMS
        ):
            raise NameNotAllowedError(f"Please choose a different {label}.")
