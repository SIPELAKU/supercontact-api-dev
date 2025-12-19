from uuid import UUID
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_model import Permission, Role
from app.repositories.permission_repository import PermissionRepository
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PermissionRepository(db)

    # CREATE
    async def create_permission(
        self,
        permission_name: str,
        role_names: Optional[List[str]] = None,
    ) -> Permission:

        async with self.db.begin():
            exists = await self.db.execute(
                select(Permission).where(Permission.permission_name == permission_name)
            )
            if exists.scalar():
                raise AppException(
                    status_code=400,
                    code=ErrorCode.BAD_REQUEST,
                    message="Permission already exists",
                )

            perm = Permission(permission_name=permission_name)
            self.db.add(perm)
            await self.db.flush()

            if role_names:
                await self._assign_roles_by_name_internal(perm.id, role_names)

        await self.db.refresh(perm)
        return perm

    # LIST (PAGINATED)
    async def get_all(
        self,
        search: Optional[str],
        page: int,
        size: int,
    ):
        return await self.repo.get_all_paginated(search, page, size)

    # UPDATE
    async def update_permission(
        self,
        permission_id: UUID,
        permission_name: Optional[str] = None,
        role_names: Optional[List[str]] = None,
    ) -> Permission:

        async with self.db.begin():
            perm = await self.repo.get_by_id(permission_id)
            if not perm:
                raise AppException(
                    status_code=404,
                    code=ErrorCode.NOT_FOUND,
                    message="Permission not found",
                )

            if permission_name and permission_name != perm.permission_name:
                exists = await self.db.execute(
                    select(Permission).where(
                        Permission.permission_name == permission_name,
                        Permission.id != permission_id,
                    )
                )
                if exists.scalar():
                    raise AppException(
                        status_code=400,
                        code=ErrorCode.BAD_REQUEST,
                        message="Permission already exists",
                    )

                perm.permission_name = permission_name

            if role_names is not None:
                await self._assign_roles_by_name_internal(perm.id, role_names)

        await self.db.refresh(perm)
        return perm

    # DELETE
    async def delete_permission(self, permission_id: UUID):
        perm = await self.repo.get_by_id(permission_id)
        if not perm:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Permission not found",
            )

        await self.db.delete(perm)
        await self.db.commit()

    # INTERNAL
    async def _assign_roles_by_name_internal(
        self,
        permission_id: UUID,
        role_names: List[str],
    ):
        result = await self.db.execute(
            select(Role).where(Role.role_name.in_(role_names))
        )
        roles = result.scalars().all()

        found = {r.role_name for r in roles}
        missing = set(role_names) - found

        if missing:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message=f"Roles not found: {list(missing)}",
            )

        await self.repo.overwrite_roles(
            permission_id,
            [r.id for r in roles],
        )
