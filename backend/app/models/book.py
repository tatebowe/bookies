from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    google_books_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    authors = Column(
        String,
        nullable=True,
    )

    description = Column(
        String,
        nullable=True,
    )

    isbn = Column(
        String,
        nullable=True,
    )

    published_date = Column(
        String,
        nullable=True,
    )

    page_count = Column(
        Integer,
        nullable=True,
    )

    language = Column(
        String,
        nullable=True,
    )

    categories = Column(
        String,
        nullable=True,
    )

    thumbnail_url = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # selections = relationship(
    # "BookSelection",
    # back_populates="book",


# )

# suggestions = relationship(
# "BookSuggestion",
# back_populates="book",
# )
