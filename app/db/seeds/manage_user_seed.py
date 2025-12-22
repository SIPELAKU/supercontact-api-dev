import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.models.user_model import User
from app.models.manage_user_model import ManageUser, UserLevel, UserStatus, Position
from app.models.role_model import Role
from app.models.branch_model import Branch
from app.models.department_enum import DepartmentEnum

DATABASE_URL = "postgresql+asyncpg://postgres:codedavid18@localhost:5433/supercontact"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

MANAGE_USER_MAP = {
    "superadmin@company.com": {
        "role": "SuperAdmin",
        "user_level": UserLevel.MANAGER,
        "position": None,
        "department": DepartmentEnum.ENGINEERING,
        "branch": "Backend",
    },
    "admin@company.com": {
        "role": "Admin",
        "user_level": UserLevel.MANAGER,
        "position": Position.HR_GENERALIST,
        "department": DepartmentEnum.HUMAN_RESOURCES,
        "branch": "Recruitment",
    },
}


async def seed_manage_users():
    async with AsyncSessionLocal() as session:
        for email, cfg in MANAGE_USER_MAP.items():

            user = (
                await session.execute(select(User).where(User.email == email))
            ).scalar_one_or_none()

            if not user:
                print(f"⚠️ User not found: {email}")
                continue

            exists = (
                await session.execute(
                    select(ManageUser).where(ManageUser.user_id == user.id)
                )
            ).scalar_one_or_none()

            if exists:
                print(f"⚠️ ManageUser exists: {email}")
                continue

            role = (
                await session.execute(select(Role).where(Role.role_name == cfg["role"]))
            ).scalar_one()

            branch = (
                await session.execute(
                    select(Branch).where(
                        Branch.name == cfg["branch"],
                        Branch.department == cfg["department"],
                    )
                )
            ).scalar_one()

            session.add(
                ManageUser(
                    id=uuid4(),
                    user_id=user.id,
                    role_id=role.id,
                    branch_id=branch.id,
                    user_level=cfg["user_level"],
                    status=UserStatus.ACTIVE,
                    position=cfg["position"],
                )
            )

            print(f"✅ ManageUser created: {email}")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_manage_users())
