import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import User, Todo
from app.db.base import Base
from app.main import app
from app.api.dependencies import get_session, get_current_user, get_user_service
from app.core.security.password_hasher import PwdlibPasswordHasher
from app.core.config import Settings, get_settings
from app.exceptions.user_exceptions import InvalidCredentialsError, UserNotFoundError
from app.exceptions.security_exceptions import HTTPValidationException
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.services.user_service import UserService


SQLALCHEMY_TEST_URL = "sqlite:///./test_db.db"

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def database_setup_cleanup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        transaction.rollback()
        session.close()
        connection.close()


@pytest.fixture()
def test_user(session):
    user = User(
        email="juan@gmail.com",
        username="juanperez",
        first_name="Juan",
        last_name="Perez",
        hashed_password=PwdlibPasswordHasher().generate_hash("juan123").hashed_password,
        phone_number=11223344,
        role="user",
    )
    session.add(user)
    session.flush()
    session.refresh(user)
    return user


@pytest.fixture()
def test_admin(session):
    admin = User(
        email="john@gmail.com",
        username="johnpeters",
        first_name="John",
        last_name="Peters",
        hashed_password=PwdlibPasswordHasher().generate_hash("john123").hashed_password,
        phone_number=111222333,
        role="admin",
    )
    session.add(admin)
    session.flush()
    session.refresh(admin)
    return admin


@pytest.fixture()
def test_todo(session, test_user):
    todo = Todo(
        title="Do laundry",
        description="Everything is dirty",
        priority=1,
        owner_id=test_user.id,
    )
    session.add(todo)
    session.flush()
    session.refresh(todo)
    return todo


@pytest.fixture()
def user_service(session):
    return UserService(
        SQLAlchemyUserRepository(session),
        PwdlibPasswordHasher(),
        session,
    )


@pytest.fixture()
def valid_todo_payload():
    return {
        "title": "A new todo",
        "description": "This is a todo",
        "priority": 1,
        "complete": False,
    }


@pytest.fixture()
def client(session):
    """
    Return TestClient with dependency overrides for settings, db and current_user.
    """

    def get_test_settings():
        return Settings(
            SECRET_KEY="some-secret-key-long-enough-hehe",
            DATABASE_URL=SQLALCHEMY_TEST_URL,
        )

    def _make_client(user: User | None = None):
        def override_get_session():
            yield session

        async def override_get_current_user():
            if user is None:
                raise HTTPValidationException(
                    status_code=401,
                    detail="Authorization failed."
                    )
            return user

        app.dependency_overrides[get_session] = override_get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_settings] = get_test_settings
        return TestClient(app)

    yield _make_client
    app.dependency_overrides.clear()


@pytest.fixture()
def mock_security(monkeypatch):

    class MockUser:
        id = 1
        email = "juan@gmail.com"
        username = "juanperez"
        first_name = "Juan"
        last_name = "Perez"
        hashed_password = "hashedpassjuan123"
        phone_number = 11223344
        role = "user"

    class MockUserService:
        def authenticate(self, credentials_data):
            if credentials_data.username != "juanperez":
                raise UserNotFoundError()
            if (
                credentials_data.username == "juanperez"
                and credentials_data.password == "secret"
            ):
                return MockUser()
            raise InvalidCredentialsError()

    def mock_create_access_token(data: dict, expiration_time_minutes):
        return "jwtpayload.jwtheader.jwtsignature"

    app.dependency_overrides[get_user_service] = lambda: MockUserService()
    monkeypatch.setattr("app.api.v1.auth.create_access_token", mock_create_access_token)
