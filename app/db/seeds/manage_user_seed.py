import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

from app.models.user_model import User, UserStatus, UserLevel
from app.models.role_model import Role
from app.models.department_model import Department
from app.models.branch_model import Branch
from app.utils.hashing import Hasher


DATABASE_URL = (
    "postgresql+asyncpg://postgres:codedavid18@localhost:5433/user_management"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_roles(session: AsyncSession):
    role_names = ["SuperAdmin", "Admin", "Manager", "Staff"]
    roles = {}

    for name in role_names:
        result = await session.execute(select(Role).where(Role.role_name == name))
        role = result.scalar_one_or_none()

        if not role:
            role = Role(id=uuid4(), role_name=name)
            session.add(role)

        roles[name] = role

    await session.commit()
    return roles


async def seed_department(session: AsyncSession):
    result = await session.execute(
        select(Department).where(Department.name == "Engineering")
    )
    dept = result.scalar_one_or_none()

    if not dept:
        dept = Department(id=uuid4(), name="Engineering")
        session.add(dept)
        await session.commit()

    return dept


async def seed_branch(session: AsyncSession, department_id):
    result = await session.execute(
        select(Branch).where(
            Branch.name == "Backend",
            Branch.department_id == department_id,
        )
    )
    branch = result.scalar_one_or_none()

    if not branch:
        branch = Branch(
            id=uuid4(),
            name="Backend",
            department_id=department_id,
        )
        session.add(branch)
        await session.commit()

    return branch


async def seed_users(
    session: AsyncSession,
    roles: dict,
    department: Department,
    branch: Branch,
):
    users = [
        # Super Admin
        dict(
            fullname="Super Admin",
            email="superadmin@company.com",
            role=roles["SuperAdmin"],
            user_level=UserLevel.MANAGER,
            department_id=None,
            branch_id=None,
        ),
        # Admin
        dict(
            fullname="Admin System",
            email="admin@company.com",
            role=roles["Admin"],
            user_level=UserLevel.MANAGER,
            department_id=department.id,
            branch_id=None,
        ),
        # Manager
        dict(
            fullname="John Manager",
            email="manager@company.com",
            role=roles["Manager"],
            user_level=UserLevel.MANAGER,
            department_id=department.id,
            branch_id=None,
        ),
        # Staff
        dict(
            fullname="Alice Staff",
            email="staff@company.com",
            role=roles["Staff"],
            user_level=UserLevel.STAFF,
            department_id=department.id,
            branch_id=branch.id,
        ),
    ]

    for data in users:
        result = await session.execute(select(User).where(User.email == data["email"]))
        exists = result.scalar_one_or_none()

        if exists:
            continue

        user = User(
            id=uuid4(),
            fullname=data["fullname"],
            email=data["email"],
            password=Hasher.hash_password("password"),
            role_id=data["role"].id,
            department_id=data["department_id"],
            branch_id=data["branch_id"],
            user_level=data["user_level"],
            status=UserStatus.ACTIVE,
        )
        session.add(user)

    await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        roles = await seed_roles(session)
        department = await seed_department(session)
        branch = await seed_branch(session, department.id)
        await seed_users(session, roles, department, branch)

    print("✅ Seeding selesai")


if __name__ == "__main__":
    asyncio.run(main())
