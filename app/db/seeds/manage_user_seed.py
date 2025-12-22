import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.models.user_model import User
from app.models.manage_user_model import ManageUser, UserLevel, UserStatus, Position
from app.models.role_model import Role
from app.models.department_model import Department

DATABASE_URL = "postgresql+asyncpg://postgres:codedavid18@localhost:5433/supercontact"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_manage_users(session: AsyncSession):
    MANAGE_USER_MAP = {
        "superadmin@company.com": {
            "role": "SuperAdmin",
            "user_level": UserLevel.MANAGER,
            "position": None,
        },
        "admin@company.com": {
            "role": "Admin",
            "user_level": UserLevel.MANAGER,
            "position": Position.HR_GENERALIST,
        },
        "manager@company.com": {
            "role": "Manager",
            "user_level": UserLevel.MANAGER,
            "position": Position.FRONTEND_ENGINEER,
        },
        "staff@company.com": {
            "role": "Staff",
            "user_level": UserLevel.STAFF,
            "position": Position.SUPPORT_AGENT,
        },
    }

    dept_result = await session.execute(
        select(Department).where(Department.name == "Engineering")
    )
    department = dept_result.scalar_one()

    for email, config in MANAGE_USER_MAP.items():
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"⚠️ User not found: {email}")
            continue

        result = await session.execute(
            select(ManageUser).where(ManageUser.user_id == user.id)
        )
        if result.scalar_one_or_none():
            print(f"⚠️ ManageUser already exists: {email}")
            continue

        result = await session.execute(
            select(Role).where(Role.role_name == config["role"])
        )
        role = result.scalar_one()

        manage_user = ManageUser(
            id=uuid4(),
            user_id=user.id,
            department_id=department.id,
            role_id=role.id,
            user_level=config["user_level"],
            status=UserStatus.ACTIVE,
            position=config["position"],
        )

        session.add(manage_user)
        print(f"✅ ManageUser created for {email}")

    await session.commit()


async def main():
    async with AsyncSessionLocal() as session:
        await seed_manage_users(session)

    print("ManageUser seeding completed")


if __name__ == "__main__":
    asyncio.run(main())
