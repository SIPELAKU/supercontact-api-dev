from sqlalchemy import delete, select
from app.models.role_model import Role, RolePermission
from uuid import UUID


class PermissionRepository:

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
