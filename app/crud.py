from typing import TypeVar
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session, DeclarativeBase
from pydantic import BaseModel


class DatabaseError(Exception):
    pass


DBModel = TypeVar("DBModel", bound=DeclarativeBase)


def create_entry(model_obj: DBModel, session: Session) -> DBModel:
    """
    Creates new entry in database or rolls back if it fails.
    :param model_obj: An SQLAlchemy model object.
    :param session: The database's session.
    :return: The added model object or None
    """
    try:
        session.add(model_obj)
        session.commit()
        session.refresh(model_obj)
        return model_obj
    except IntegrityError as e:
        session.rollback()
        raise DatabaseError("Integrity constraint failed") from e
    except SQLAlchemyError as e:
        session.rollback()
        raise DatabaseError(f"Failed to create new entry in database: {e}") from e
    
    


def get_all_entries(model_cls: DBModel, session: Session, *conditions) -> list[DBModel]:
    stmt = select(model_cls)
    if conditions:
        stmt = stmt.where(*conditions)
    return session.execute(stmt).scalars().all()


def get_entry(model_cls: DBModel, session: Session, *conditions, id: int | None = None) -> DBModel | None:
    if id:
        return session.get(model_cls, id)
    return session.execute(select(model_cls).where(*conditions)).scalars().first()


def update_entry(entry_id: int, model_cls: DBModel, new_data: BaseModel, session: Session) -> DBModel | None:
    db_entry = session.get(model_cls, entry_id)
    if not db_entry:
        return None
    try:
        for attr, value in new_data.model_dump(exclude_unset=True, exclude_none=True).items():
            try:
                setattr(db_entry, attr, value)
            except Exception as e:
                print(e)
        session.commit()
        session.refresh(db_entry)
        print("Entry succesfully updated.")
        return db_entry
    except SQLAlchemyError:
        session.rollback()
        return None


def delete_entry(entry_id: int, model_cls: DBModel, session: Session) -> bool:
    db_entry = session.get(model_cls, entry_id)
    if not db_entry:
        return False
    try:
        session.delete(db_entry)
        session.commit()
        print("Entry succesfully deleted.")
        return True
    except SQLAlchemyError:
        session.rollback()
        print(f"Error while deleting database entry. Rolling back. \n"
              f"Error: {e}")
        return False
