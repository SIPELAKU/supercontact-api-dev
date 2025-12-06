import os
from dotenv import load_dotenv
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ⚡ Async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# ⚡ Async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 🎯 Tambahkan ini → untuk Alembic
Base = SQLModel.metadata


# Dependency FastAPI
async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session


# Create DB tables (dipanggil saat startup)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
