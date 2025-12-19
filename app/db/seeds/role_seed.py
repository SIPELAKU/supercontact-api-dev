import asyncio
from uuid import uuid4

from sqlmodel import select

from app.db import get_async_session
from app.models import Role

ROLES = [
    ("SuperAdmin", True),
    ("Admin", True),
    ("Manager", False),
    ("Staff", False),
]


async def seed_roles():
    db_gen = get_async_session()
    db = await anext(db_gen)
    roles = []

    for role_name, is_system in ROLES:
        result = await db.execute(select(Role).where(Role.role_name == role_name))
        role = result.scalar_one_or_none()

        if not role:
            role = Role(
                id=uuid4(),
                role_name=role_name,
                is_system_role=is_system,
            )
            db.add(role)

        roles.append(role)

    await db.commit()
    return roles


if __name__ == "__main__":
    print("Running database seed...")
    asyncio.run(seed_roles())
    print("Seed completed!")
