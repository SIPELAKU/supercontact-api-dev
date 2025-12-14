from sqlalchemy import select
from uuid import UUID
from app.models.role_model import Permission, Role
from app.repository.permission_repository import PermissionRepository


class PermissionService:
    def __init__(self, db):
        self.db = db
        self.repo = PermissionRepository(db)

    async def create_permission(self, permission_name: str) -> Permission:
        exists = await self.db.execute(
            select(Permission).where(Permission.permission_name == permission_name)
        )
        if exists.scalar():
            raise ValueError("Permission already exists")

        perm = Permission(permission_name=permission_name)
        self.db.add(perm)
        await self.db.commit()
        await self.db.refresh(perm)
        return perm

    async def assign_roles(
        self,
        permission_id: UUID,
        role_ids: list[UUID],
    ):
        perm = await self.repo.get_permission_by_id(permission_id)
        if not perm:
            raise ValueError("Permission not found")

        # validasi role
        result = await self.db.execute(select(Role.id).where(Role.id.in_(role_ids)))
        found_roles = set(result.scalars().all())

        missing = set(role_ids) - found_roles
        if missing:
            raise ValueError(f"Role not found: {missing}")

        await self.repo.assign_roles(permission_id, role_ids)

    async def remove_role(
        self,
        permission_id: UUID,
        role_id: UUID,
    ):
        await self.repo.remove_role(permission_id, role_id)
