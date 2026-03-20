from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[str] = mapped_column(Boolean, default=True)
    phone_number: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"<id=({self.id}), email=({self.email}), username=({self.email})>"
