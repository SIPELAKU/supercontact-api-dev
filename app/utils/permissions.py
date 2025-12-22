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
    """
    Ambil role user melalui tabel manage_users
    Alur:
    User -> ManageUser -> Role -> Permissions
    """

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
    """
    Batasi akses berdasarkan role name
    Contoh:
    Depends(require_roles("Super Admin", "Admin"))
    """

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
    """
    Batasi akses berdasarkan permission
    Support wildcard per module (contoh: user:*)
    """

    async def wrapper(role: Role = Depends(get_current_role)) -> Role:
        user_permissions = {p.permission_name for p in role.permissions}

        for required in required_permissions:
            # permission exact
            if required in user_permissions:
                continue

            # permission wildcard module
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
