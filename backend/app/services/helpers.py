from typing import TypeVar

from sqlalchemy.orm import DeclarativeBase, Session

ModelType = TypeVar(
    "ModelType",
    bound=DeclarativeBase,
)


def get_by_id(
    db: Session,
    model: type[ModelType],
    object_id: int,
) -> ModelType | None:
    return db.get(
        model,
        object_id,
    )


def exists(
    db: Session,
    model: type[ModelType],
    **filters: object,
) -> bool:
    return db.query(model).filter_by(**filters).first() is not None


def save_and_refresh(
    db: Session,
    obj,
):
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj
