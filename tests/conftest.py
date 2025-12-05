import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.main import app
from tests.db import seed_all_test
from tests.utils.auth import authenticate_test_user

DATABASE_TEST_URL = "sqlite+aiosqlite:///tests/db/db_test.db"
async_engine = create_async_engine(
    DATABASE_TEST_URL,
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_engine,
)


@pytest_asyncio.fixture
async def db_async_session():
    # create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # session
    async with async_session_maker() as session:
        await seed_all_test(session)
        yield session

    # drop tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def override_get_async_session():
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_async_session):
    # override dependency session
    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_token(client):
    return await authenticate_test_user(client)


@pytest.fixture
def hello():
    def _say(name: str):
        return f"Hello {name}"

    return _say
