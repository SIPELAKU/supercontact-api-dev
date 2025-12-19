from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_model import Permission, RolePermission


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_permission_by_id(self, permission_id: UUID):
        result = await self.db.execute(
            select(Permission)
            .where(Permission.id == permission_id)
            .options(selectinload(Permission.roles))
        )
        return result.scalar_one_or_none()

    async def remove_role(
        self,
        permission_id: UUID,
        role_id: UUID,
    ):
        await self.db.execute(
            delete(RolePermission).where(
                RolePermission.permission_id == permission_id,
                RolePermission.role_id == role_id,
            )
        )
        await self.db.commit()
