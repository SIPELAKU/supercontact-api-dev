import asyncio
from uuid import uuid4

from sqlmodel import select

from app.db import get_async_session
from app.models import (
    Branch,
    ManageUser,
    Position,
    Role,
    User,
    UserLevel,
    UserStatus,
)
from app.models.department_enum import DepartmentEnum

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
    db_gen = get_async_session()
    db = await anext(db_gen)
    for email, cfg in MANAGE_USER_MAP.items():
        user = (
            await db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()

        if not user:
            print(f"⚠️ User not found: {email}")
            continue

        exists = (
            await db.execute(select(ManageUser).where(ManageUser.user_id == user.id))
        ).scalar_one_or_none()

        if exists:
            print(f"⚠️ ManageUser exists: {email}")
            continue

        role = (
            await db.execute(select(Role).where(Role.role_name == cfg["role"]))
        ).scalar_one()

        branch = (
            await db.execute(
                select(Branch).where(
                    Branch.name == cfg["branch"],
                    Branch.department == cfg["department"],
                )
            )
        ).scalar_one()

        db.add(
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

    await db.commit()


if __name__ == "__main__":
    print("Running database seed...")
    asyncio.run(seed_manage_users())
    print("Seed completed!")
