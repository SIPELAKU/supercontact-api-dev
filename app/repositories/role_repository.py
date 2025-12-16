from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Role, RolePermission
from app.repositories import PermissionRepository


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_all_roles(self) -> List[Role]:
        query = select(Role).options(
            selectinload(Role.permissions),
            selectinload(Role.users),
        )
        result = await self.db.exec(query)
        return result.all()

    async def get_role_by_id(self, role_id: UUID) -> Optional[Role]:
        query = (
            select(Role)
            .where(Role.id == role_id)
            .options(
                selectinload(Role.permissions),
                selectinload(Role.users),
            )
        )
        result = await self.db.exec(query)
        return result.first()

    async def update_role(self, role_id: UUID, data: dict) -> Optional[Role]:
        role = await self.get_role_by_id(role_id)
        if not role:
            return None

        for key, value in data.items():
            setattr(role, key, value)

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete_role(self, role_id: UUID) -> bool:
        role = await self.get_role_by_id(role_id)
        if not role:
            return False

        await self.db.exec(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )

        await self.db.delete(role)
        await self.db.commit()
        return True

    async def assign_permission(self, role_id: UUID, permission_id: UUID):
        role = await self.get_role_by_id(role_id)
        if not role:
            raise ValueError("Role not found")

        perm_repo = PermissionRepository(self.db)
        permission = await perm_repo.get_permission_by_id(permission_id)
        if not permission:
            raise ValueError("Permission not found")

        existing = await self.db.exec(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )

        if existing.first():
            return existing.first()

        link = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def remove_permission(self, role_id: UUID, permission_id: UUID):
        await self.db.exec(
            delete(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        await self.db.commit()
        return True

    async def get_role_permissions(self, role_id: UUID):
        role = await self.get_role_by_id(role_id)
        return role.permissions if role else []
