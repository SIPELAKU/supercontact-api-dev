import asyncio
from uuid import uuid4

from sqlmodel import select

from app.db import get_async_session
from app.models import Branch
from app.models.department_enum import DepartmentEnum

BRANCHES = {
    DepartmentEnum.MARKETING: ["Digital", "Brand"],
    DepartmentEnum.SALES: ["Retail", "Enterprise"],
    DepartmentEnum.ENGINEERING: ["Backend", "Frontend"],
    DepartmentEnum.HUMAN_RESOURCES: ["Recruitment"],
    DepartmentEnum.CUSTOMER_SUPPORT: ["Tier 1", "Tier 2"],
}


async def seed_branches():
    db_gen = get_async_session()
    db = await anext(db_gen)
    for department, branch_names in BRANCHES.items():
        for name in branch_names:
            result = await db.execute(
                select(Branch).where(
                    Branch.name == name,
                    Branch.department == department,
                )
            )
            if result.scalar_one_or_none():
                continue

            db.add(
                Branch(
                    id=uuid4(),
                    name=name,
                    department=department,
                )
            )

    await db.commit()
    print("✅ Branch seeded")


if __name__ == "__main__":
    print("Running database seed...")
    asyncio.run(seed_branches())
    print("Seed completed!")
