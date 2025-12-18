import asyncio
from uuid import uuid4

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.role_model import Role


DATABASE_URL = "postgresql+asyncpg://postgres:codedavid18@localhost:5433/supercontact"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


ROLES = [
    ("SuperAdmin", True),
    ("Admin", True),
    ("Manager", False),
    ("Staff", False),
]


async def seed_roles(session: AsyncSession):
    roles = []

    for role_name, is_system in ROLES:
        result = await session.execute(select(Role).where(Role.role_name == role_name))
        role = result.scalar_one_or_none()

        if not role:
            role = Role(
                id=uuid4(),
                role_name=role_name,
                is_system_role=is_system,
            )
            session.add(role)

        roles.append(role)

    await session.commit()
    return roles


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        await seed_roles(session)

    print("Seed roles selesai")


if __name__ == "__main__":
    asyncio.run(main())
