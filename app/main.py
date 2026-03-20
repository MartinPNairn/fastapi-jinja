from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.models import User, Todo
from app.db.base import Base
from app.db.session import  engine
from app.api.router import router_aggregator


BASE_DIR = Path(__file__).resolve().parent  # points to app/
STATIC_DIR = BASE_DIR / "frontend" / "static"



def create_app():
    app = FastAPI(
        title="A Marvellous API for to-do's",
        version="0.1"
    )

    app.include_router(router_aggregator)

    app.mount("/frontend/static", StaticFiles(directory=STATIC_DIR), name="static")

    Base.metadata.create_all(bind=engine)

    return app


app = create_app()
