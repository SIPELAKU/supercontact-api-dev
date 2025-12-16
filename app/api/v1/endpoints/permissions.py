from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.permission_schema import (
    PermissionCreate,
    PermissionRead,
    PermissionReadWithRoles,
    PermissionAssignRoles,
)
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/permission", tags=["Permissions"])


def get_service(db: AsyncSession = Depends(get_async_session)):
    return PermissionService(db)


@router.post(
    "",
    response_model=PermissionRead,
    # dependencies=[Depends(require_permissions("permission:create"))],
)
async def create_permission(
        data: PermissionCreate,
        service: PermissionService = Depends(get_service),
):
    return await service.create_permission(data.permission_name)


@router.get(
    "/{permission_id}",
    response_model=PermissionReadWithRoles,
    # dependencies=[Depends(require_permissions("permission:read"))],
)
async def get_permission(
        permission_id: UUID,
        service: PermissionService = Depends(get_service),
):
    return await service.repo.get_permission_by_id(permission_id)


@router.post(
    "/{permission_id}/roles",
    # dependencies=[Depends(require_permissions("permission:assign-roles"))],
)
async def assign_roles(
        permission_id: UUID,
        data: PermissionAssignRoles,
        service: PermissionService = Depends(get_service),
):
    await service.assign_roles(permission_id, data.role_ids)
    return {"message": "Roles assigned to permission"}


@router.delete(
    "/{permission_id}/roles/{role_id}",
    # dependencies=[Depends(require_permissions("permission:remove-role"))],
)
async def remove_role(
        permission_id: UUID,
        role_id: UUID,
        service: PermissionService = Depends(get_service),
):
    await service.remove_role(permission_id, role_id)
    return {"message": "Role removed from permission"}
