from math import ceil
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.app_exception import AppException
from app.schemas.role_permission_schema import RoleCreate, RoleUpdate, RoleQuery
from app.schemas import ErrorCode
from app.models.role_model import Role
from app.repository.role_permission_repository import RolePermissionRepository


class RolePermissionService:
    def __init__(self, db: AsyncSession):
        self.repo = RolePermissionRepository(db)

    async def create_role(self, payload: RoleCreate):

        existing = await self.repo.get_role_by_name(payload.name)
        if existing:
            raise AppException(
                status_code=400,
                code=ErrorCode.ALREADY_EXISTS,
                message="Role name already exists",
            )

        new_role = Role(name=payload.name)

        permissions = [perm.permission for perm in (payload.permissions or [])]

        role = await self.repo.create_role(new_role, permissions)
        return role

    async def get_roles(self, query_params: RoleQuery):
        role_query = RoleQuery(**query_params.model_dump())

        roles, total = await self.repo.get_roles(role_query)
        total_pages = ceil(total / query_params.limit) if total else 1

        return {
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": total_pages,
            "roles": roles,
        }

    async def get_role_by_id(self, role_id: UUID):
        role = await self.repo.get_role_by_id(role_id)
        if not role:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Role not found",
            )
        return role

    async def update_role(self, role_id: UUID, payload: RoleUpdate):
        role = await self.repo.get_role_by_id(role_id)
        if not role:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Role not found",
            )

        if payload.name and payload.name != role.name:
            existing = await self.repo.get_role_by_name(payload.name)
            if existing:
                raise AppException(
                    status_code=400,
                    code=ErrorCode.ALREADY_EXISTS,
                    message="Role name already exists",
                )

        updated_role = await self.repo.update_role(role, payload)
        return updated_role

    async def delete_role(self, role_id: UUID):
        role = await self.repo.get_role_by_id(role_id)
        if not role:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Role not found",
            )

        await self.repo.delete_role(role)
        return {"message": "Role deleted successfully"}
