import asyncio
from uuid import uuid4

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.department_model import Department
from app.models.branch_model import Branch


DATABASE_URL = (
    "postgresql+asyncpg://postgres:codedavid18@localhost:5433/user_management"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


BRANCHES = {
    "Marketing": ["Digital", "Brand"],
    "Sales": ["Retail", "Enterprise"],
    "Engineering": ["Backend", "Frontend"],
    "Human Resources": ["Recruitment"],
    "Customer Support": ["Tier 1", "Tier 2"],
}


async def seed_branches(session: AsyncSession):
    for dept_name, branch_names in BRANCHES.items():
        # ambil department
        result = await session.execute(
            select(Department).where(Department.name == dept_name)
        )
        department = result.scalar_one_or_none()

        if not department:
            continue

        for branch_name in branch_names:
            result = await session.execute(
                select(Branch).where(
                    Branch.name == branch_name,
                    Branch.department_id == department.id,
                )
            )
            exists = result.scalar_one_or_none()

            if exists:
                continue

            branch = Branch(
                id=uuid4(),
                name=branch_name,
                department_id=department.id,
            )
            session.add(branch)

    await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        await seed_branches(session)

    print("Seeding branches selesai!")


if __name__ == "__main__":
    asyncio.run(main())
