from uuid import UUID
from sqlalchemy import select

from app.models.role_model import Permission, Role
from app.repositories.permission_repository import PermissionRepository
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode


class PermissionService:
    def __init__(self, db):
        self.db = db
        self.repo = PermissionRepository(db)

    # ============================
    # CREATE (WITH ROLE ACCESS)
    # ============================

    async def create_permission(
        self,
        permission_name: str,
        role_names: list[str] | None = None,
    ) -> Permission:

        exists = await self.db.execute(
            select(Permission).where(Permission.permission_name == permission_name)
        )
        if exists.scalar():
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Permission already exists",
            )

        # 1️⃣ CREATE PERMISSION
        perm = Permission(permission_name=permission_name)
        self.db.add(perm)
        await self.db.commit()
        await self.db.refresh(perm)

        # 2️⃣ ASSIGN ROLES (OPTIONAL)
        if role_names is not None:
            await self._assign_roles_by_name_internal(perm.id, role_names)

        return perm

    # ============================
    # UPDATE (🔥 SAME BEHAVIOR AS CREATE)
    # ============================

    async def update_permission(
        self,
        permission_id: UUID,
        permission_name: str | None = None,
        role_names: list[str] | None = None,
    ) -> Permission:

        perm = await self.repo.get_permission_by_id(permission_id)
        if not perm:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Permission not found",
            )

        # 1️⃣ UPDATE NAME
        if permission_name:
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

        await self.db.commit()
        await self.db.refresh(perm)

        # 2️⃣ UPDATE ROLE ACCESS (OVERWRITE)
        if role_names is not None:
            await self._assign_roles_by_name_internal(perm.id, role_names)

        return perm

    # ============================
    # DELETE
    # ============================

    async def delete_permission(self, permission_id: UUID):
        perm = await self.repo.get_permission_by_id(permission_id)
        if not perm:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Permission not found",
            )

        await self.db.delete(perm)
        await self.db.commit()

    # ============================
    # ASSIGN ROLES (UUID)
    # ============================

    async def assign_roles(
        self,
        permission_id: UUID,
        role_ids: list[UUID],
    ):
        perm = await self.repo.get_permission_by_id(permission_id)
        if not perm:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Permission not found",
            )

        result = await self.db.execute(select(Role.id).where(Role.id.in_(role_ids)))
        found = set(result.scalars().all())
        missing = set(role_ids) - found

        if missing:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message=f"Roles not found: {list(missing)}",
            )

        await self.repo.assign_roles(permission_id, role_ids)

    # ============================
    # ASSIGN ROLES (ROLE_NAME)
    # ============================

    async def assign_roles_by_name(
        self,
        permission_id: UUID,
        role_names: list[str],
    ):
        perm = await self.repo.get_permission_by_id(permission_id)
        if not perm:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Permission not found",
            )

        await self._assign_roles_by_name_internal(permission_id, role_names)

    # ============================
    # INTERNAL HELPER (🔥 REUSED)
    # ============================

    async def _assign_roles_by_name_internal(
        self,
        permission_id: UUID,
        role_names: list[str],
    ):
        result = await self.db.execute(
            select(Role).where(Role.role_name.in_(role_names))
        )
        roles = result.scalars().all()

        found_names = {r.role_name for r in roles}
        missing = set(role_names) - found_names

        if missing:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message=f"Roles not found: {list(missing)}",
            )

        await self.repo.assign_roles(
            permission_id,
            [r.id for r in roles],
        )

    # ============================
    # REMOVE ROLE
    # ============================

    async def remove_role(
        self,
        permission_id: UUID,
        role_id: UUID,
    ):
        await self.repo.remove_role(permission_id, role_id)
