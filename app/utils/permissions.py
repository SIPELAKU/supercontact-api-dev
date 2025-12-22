from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import auth_require
from app.db import get_async_session
from app.exceptions import AppException
from app.models import User, Role, ManageUser
from app.schemas import ErrorCode


async def get_current_role(
    user: User = Depends(auth_require),
    db: AsyncSession = Depends(get_async_session),
) -> Role:

    stmt = (
        select(ManageUser)
        .where(ManageUser.user_id == user.id)
        .options(selectinload(ManageUser.role).selectinload(Role.permissions))
    )

    result = await db.execute(stmt)
    manage_user = result.scalar_one_or_none()

    if not manage_user:
        raise AppException(
            status_code=403,
            code=ErrorCode.FORBIDDEN,
            message="User is not registered in manage user",
        )

    if not manage_user.role:
        raise AppException(
            status_code=403,
            code=ErrorCode.FORBIDDEN,
            message="User has no role assigned",
        )

    return manage_user.role


def require_roles(*allowed_roles: str):

    async def wrapper(role: Role = Depends(get_current_role)) -> Role:
        if role.role_name not in allowed_roles:
            raise AppException(
                status_code=403,
                code=ErrorCode.FORBIDDEN,
                message=f"Role '{role.role_name}' is not allowed",
            )
        return role

    return wrapper


def require_permissions(*required_permissions: str):

    async def wrapper(role: Role = Depends(get_current_role)) -> Role:
        user_permissions = {p.permission_name for p in role.permissions}

        for required in required_permissions:
            # exact permission
            if required in user_permissions:
                continue

            # wildcard module
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
