import asyncio
from uuid import uuid4

from sqlmodel import select

from app.db import get_async_session
from app.models.role_model import Permission

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


async def seed_permissions():
    db_gen = get_async_session()
    db = await anext(db_gen)
    for old, new in OLD_TO_NEW.items():
        result = await db.execute(
            select(Permission).where(Permission.permission_name == old)
        )
        perm = result.scalar_one_or_none()

        if perm:
            perm.permission_name = new

    for perm_name in PERMISSIONS:
        result = await db.execute(
            select(Permission).where(Permission.permission_name == perm_name)
        )
        exists = result.scalar_one_or_none()

        if exists:
            continue

        db.add(
            Permission(
                id=uuid4(),
                permission_name=perm_name,
            )
        )

    await db.commit()


if __name__ == "__main__":
    print("Running database seed...")
    asyncio.run(seed_permissions())
    print("Seed completed!")
