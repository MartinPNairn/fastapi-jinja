from app.core.config import get_settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = get_settings()
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
