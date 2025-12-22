import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.models.branch_model import Branch
from app.models.department_enum import DepartmentEnum

DATABASE_URL = "postgresql+asyncpg://postgres:codedavid18@localhost:5433/supercontact"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

BRANCHES = {
    DepartmentEnum.MARKETING: ["Digital", "Brand"],
    DepartmentEnum.SALES: ["Retail", "Enterprise"],
    DepartmentEnum.ENGINEERING: ["Backend", "Frontend"],
    DepartmentEnum.HUMAN_RESOURCES: ["Recruitment"],
    DepartmentEnum.CUSTOMER_SUPPORT: ["Tier 1", "Tier 2"],
}


async def seed_branches():
    async with AsyncSessionLocal() as session:
        for department, branch_names in BRANCHES.items():
            for name in branch_names:
                result = await session.execute(
                    select(Branch).where(
                        Branch.name == name,
                        Branch.department == department,
                    )
                )
                if result.scalar_one_or_none():
                    continue

                session.add(
                    Branch(
                        id=uuid4(),
                        name=name,
                        department=department,
                    )
                )

        await session.commit()
        print("✅ Branch seeded")


if __name__ == "__main__":
    asyncio.run(seed_branches())
