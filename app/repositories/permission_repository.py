from uuid import UUID
from typing import List, Optional

from sqlalchemy import delete, select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_model import Permission, RolePermission


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, permission_id: UUID) -> Optional[Permission]:
        result = await self.db.execute(
            select(Permission)
            .where(Permission.id == permission_id)
            .options(selectinload(Permission.roles))
        )
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        search: Optional[str],
        page: int,
        size: int,
    ):
        stmt = select(Permission).options(selectinload(Permission.roles))

        if search:
            stmt = stmt.where(Permission.permission_name.ilike(f"%{search}%"))

        total = await self.db.scalar(select(func.count()).select_from(stmt.subquery()))

        stmt = stmt.offset((page - 1) * size).limit(size)

        result = await self.db.execute(stmt)

        return {
            "items": result.scalars().all(),
            "total": total,
            "page": page,
            "size": size,
        }

    async def overwrite_roles(
        self,
        permission_id: UUID,
        role_ids: List[UUID],
    ):
        await self.db.execute(
            delete(RolePermission).where(RolePermission.permission_id == permission_id)
        )

        for role_id in role_ids:
            self.db.add(
                RolePermission(
                    permission_id=permission_id,
                    role_id=role_id,
                )
            )
