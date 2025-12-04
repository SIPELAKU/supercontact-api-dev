import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

from app.db.session import get_session
from app.main import app
from tests.db.seed_all_test import seed_all_test
from tests.utils.auth import authenticate_test_user

DATABASE_TEST_URL = "sqlite:///tests/db/db_test.db"
engine = create_engine(DATABASE_TEST_URL, connect_args={"check_same_thread": False})


@pytest.fixture
def db_session():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        seed_all_test(session)
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    return TestClient(app)


@pytest.fixture
def auth_token(client):
    return authenticate_test_user(client)


@pytest.fixture
def hello():
    def _say(name: str):
        return f"Hello {name}"

    return _say
