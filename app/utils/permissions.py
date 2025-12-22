from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import auth_require
from app.db import get_async_session
from app.exceptions import AppException
from app.models import Role, User
from app.schemas import ErrorCode


async def get_current_role(
        user: User = Depends(auth_require),
        db: AsyncSession = Depends(get_async_session),
) -> Role:
    if not user.role_id:
        raise AppException(
            status_code=403,
            code=ErrorCode.FORBIDDEN,
            message="User has no role assigned",
        )

    stmt = (
        select(Role)
        .where(Role.id == user.role_id)
        .options(selectinload(Role.permissions))
    )

    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise AppException(
            status_code=403,
            code=ErrorCode.FORBIDDEN,
            message="User role not found",
        )

    return role


def require_roles(*allowed_roles: str):
    async def wrapper(role: Role = Depends(get_current_role)):
        if role.role_name not in allowed_roles:
            raise AppException(
                status_code=403,
                code=ErrorCode.FORBIDDEN,
                message=f"Role '{role.role_name}' is not allowed",
            )
        return role

    return wrapper


def require_permissions(*required_permissions: str):
    async def wrapper(role: Role = Depends(get_current_role)):

        user_permissions = {p.permission_name for p in role.permissions}

        for required in required_permissions:
            if required in user_permissions:
                continue

            module = required.split(":")[0]
            if f"{module}:*" in user_permissions:
                continue

            raise AppException(
                status_code=403,
                code=ErrorCode.FORBIDDEN,
                message=f"Missing permission: {required}",
            )

        return role

    return wrapper
