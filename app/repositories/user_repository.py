from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self) -> list[User]:
        return list(self._session.execute(select(User)).scalars().all())

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def create(self, user_data: dict) -> User:
        new_user = User(**user_data)
        self._session.add(new_user)
        return new_user

    def update(self, user_id: int, user_data: dict) -> User | None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**user_data)
            .returning(User)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def delete(self, user_id: int) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = self._session.execute(stmt)
        return result.rowcount > 0
