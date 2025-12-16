import asyncio
from uuid import uuid4

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.department_model import Department


DATABASE_URL = (
    "postgresql+asyncpg://postgres:codedavid18@localhost:5433/user_management"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


DEPARTMENTS = [
    "Marketing",
    "Sales",
    "Engineering",
    "Human Resources",
    "Customer Support",
]


async def seed_departments(session: AsyncSession):
    departments = []

    for name in DEPARTMENTS:
        result = await session.execute(
            select(Department).where(Department.name == name)
        )
        department = result.scalar_one_or_none()

        if not department:
            department = Department(
                id=uuid4(),
                name=name,
            )
            session.add(department)

        departments.append(department)

    await session.commit()
    return departments


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        await seed_departments(session)

    print("✅ Department seeding selesai!")


if __name__ == "__main__":
    asyncio.run(main())
