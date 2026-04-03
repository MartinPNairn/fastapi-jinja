import os

from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import User, Todo
from app.db.base import Base
from app.main import app
from app.api.dependencies import get_db, get_current_user
from app.core.security import create_password_hash


load_dotenv()

SQLALCHEMY_TEST_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

SECRET_KEY = os.getenv("SECRET_KEY")
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM")


@pytest.fixture(scope="session", autouse=True)
def database_setup_cleanup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        transaction.rollback()
        db.close()
        connection.close()


@pytest.fixture()
def test_user(db):
    user = User(
        email="juan@gmail.com",
        username="juanperez",
        first_name="Juan",
        last_name="Perez",
        hashed_password=create_password_hash("juan123"),
        phone_number=11223344,
        role="user",
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


@pytest.fixture()
def test_admin(db):
    admin = User(
        email="john@gmail.com",
        username="johnpeters",
        first_name="John",
        last_name="Peters",
        hashed_password=create_password_hash("john123"),
        phone_number=111222333,
        role="admin",
    )
    db.add(admin)
    db.flush()
    db.refresh(admin)
    return admin


@pytest.fixture()
def test_todo(db, test_user):
    todo = Todo(
        title="Do laundry",
        description="Everything is dirty",
        priority=1,
        owner_id=test_user.id,
    )
    db.add(todo)
    db.flush()
    db.refresh(todo)
    return todo


@pytest.fixture()
def client(db):
    """
    Return TestClient with dependency overrides for db and current_user.
    """

    def _make_client(user: User | None = None):
        def override_get_db():
            yield db

        async def override_get_current_user():
            return user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        return TestClient(app)

    yield _make_client

    app.dependency_overrides.clear()


@pytest.fixture()
def mock_security(monkeypatch):

    class MockUser:
        email = "juan@gmail.com"
        username = "juanperez"
        first_name = "Juan"
        last_name = "Perez"
        hashed_password = "hashedpassjuan123"
        phone_number = 11223344
        role = "user"

    def mock_authenticate_user(username: str, password: str, db):
        if username and password == "secret":
            return MockUser()
        return False
    
    def mock_create_access_token(data: dict, expires_delta):
        return "jwtpayload.jwtheader.jwtsignature"
    
    monkeypatch.setattr("app.api.v1.auth.authenticate_user", mock_authenticate_user)
    monkeypatch.setattr("app.api.v1.auth.create_access_token", mock_create_access_token)
