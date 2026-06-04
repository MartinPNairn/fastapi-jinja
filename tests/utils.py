from typing import TypeVar
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import select


T = TypeVar("T", bound=DeclarativeBase)


def get_fresh_entry_by_primary_key(
    session: Session,
    model: type[T],
    primary_key_value: int,
) -> T | None:
    session.expire_all()
    return session.get(model, primary_key_value)


def get_fresh_entry_with_conditions(
    session: Session,
    model: type[T],
    *conditions,
) -> T | None:
    session.expire_all()
    stmt = select(model).where(*conditions)
    return session.execute(stmt).scalar_one_or_none()


def entry_is_in_db(
    session: Session,
    model: type[T],
    primary_key_value: int,
) -> bool:
    session.expire_all()
    return session.get(model, primary_key_value) is not None
