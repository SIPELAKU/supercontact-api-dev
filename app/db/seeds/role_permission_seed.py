import asyncio
from uuid import uuid4

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.role_model import Role, Permission, RolePermission

DATABASE_URL = (
    "postgresql+asyncpg://postgres:codedavid18@localhost:5433/user_management"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

ROLE_PERMISSION_MAP = {
    "SuperAdmin": [
        "user:*",
        "role:*",
        "department:*",
    ],
    "Admin": [
        "user:*",
        "department:*",
    ],
    "Manager": [
        "user:read",
        "department:*",
    ],
    "Staff": [
        "user:read",
    ],
}


async def seed_role_permissions(session: AsyncSession):
    for role_name, permission_names in ROLE_PERMISSION_MAP.items():

        result = await session.execute(select(Role).where(Role.role_name == role_name))
        role = result.scalar_one_or_none()

        if not role:
            print(f"⚠️ Role '{role_name}' not found, skipped")
            continue

        for perm_name in permission_names:
            result = await session.execute(
                select(Permission).where(Permission.permission_name == perm_name)
            )
            permission = result.scalar_one_or_none()

            if not permission:
                print(f"⚠️ Permission '{perm_name}' not found, skipped")
                continue

            result = await session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            )
            exists = result.scalar_one_or_none()

            if exists:
                continue

            session.add(
                RolePermission(
                    id=uuid4(),
                    role_id=role.id,
                    permission_id=permission.id,
                )
            )

    await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        await seed_role_permissions(session)

    print("✅ Role permissions synced successfully")


if __name__ == "__main__":
    asyncio.run(main())
