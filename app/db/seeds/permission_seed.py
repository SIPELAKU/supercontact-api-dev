import asyncio
from uuid import uuid4

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.role_model import Permission

DATABASE_URL = "postgresql+asyncpg://postgres:codedavid18@localhost:5433/supercontact"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

PERMISSIONS = [
    # USER
    "user:create",
    "user:read",
    "user:update",
    "user:delete",
    "user:*",
    # ROLE
    "role:create",
    "role:read",
    "role:update",
    "role:delete",
    "role:*",
    # DEPARTMENT
    "department:create",
    "department:read",
    "department:update",
    "department:delete",
    "department:*",
    # PERMISSION
    "permission:*",
]

OLD_TO_NEW = {
    # user
    "user.create": "user:create",
    "user.read": "user:read",
    "user.update": "user:update",
    "user.delete": "user:delete",
    "user.manage": "user:*",
    # department
    "department.manage": "department:*",
    # role
    "role.manage": "role:*",
}


async def seed_permissions(session: AsyncSession):
    for old, new in OLD_TO_NEW.items():
        result = await session.execute(
            select(Permission).where(Permission.permission_name == old)
        )
        perm = result.scalar_one_or_none()

        if perm:
            perm.permission_name = new

    for perm_name in PERMISSIONS:
        result = await session.execute(
            select(Permission).where(Permission.permission_name == perm_name)
        )
        exists = result.scalar_one_or_none()

        if exists:
            continue

        session.add(
            Permission(
                id=uuid4(),
                permission_name=perm_name,
            )
        )

    await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        await seed_permissions(session)

    print("Permissions seeded (branch removed)")


if __name__ == "__main__":
    asyncio.run(main())
