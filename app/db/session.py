from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

# ENGINE SETUP
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# SESSION MAKER
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# FOR SESSION
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
