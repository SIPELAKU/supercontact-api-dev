from uuid import UUID

from sqlalchemy import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.role_model import RolePermission


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_roles(
            self,
            permission_id: UUID,
            role_ids: list[UUID],
    ):
        await self.db.exec(
            delete(RolePermission).where(RolePermission.permission_id == permission_id)
        )

        for role_id in role_ids:
            self.db.add(
                RolePermission(
                    role_id=role_id,
                    permission_id=permission_id,
                )
            )

        await self.db.commit()

    async def remove_role(
            self,
            permission_id: UUID,
            role_id: UUID,
    ):
        await self.db.exec(
            delete(RolePermission).where(
                RolePermission.permission_id == permission_id,
                RolePermission.role_id == role_id,
            )
        )
        await self.db.commit()
