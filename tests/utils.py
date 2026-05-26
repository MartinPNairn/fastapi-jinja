from typing import TypeVar
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import select


T = TypeVar("T", bound=DeclarativeBase)


def get_fresh_entry_by_primary_key(
    db: Session,
    model: type[T],
    primary_key_value: int,
) -> T | None:
    db.expire_all()
    return db.get(model, primary_key_value)


def get_fresh_entry_with_conditions(
    db: Session,
    model: type[T],
    *conditions,
) -> T | None:
    db.expire_all()
    stmt = select(model).where(*conditions)
    return db.execute(stmt).scalar_one_or_none()


def entry_is_in_db(
    db: Session,
    model: type[T],
    primary_key_value: int,
) -> bool:
    db.expire_all()
    return db.get(model, primary_key_value) is not None
