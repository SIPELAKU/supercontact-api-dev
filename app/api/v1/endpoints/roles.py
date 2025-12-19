from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.role_schema import (
    RoleCreate,
    RoleUpdate,
    RoleRead,
)
from app.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])


def get_role_service(db: AsyncSession = Depends(get_async_session)):
    return RoleService(db)


@router.post(
    "",
    response_model=RoleRead,
    # dependencies=[Depends(require_permissions("role:create"))],
)
async def create_role(
        data: RoleCreate,
        service: RoleService = Depends(get_role_service),
):
    return await service.create_role(
        role_name=data.role_name,
        is_system_role=data.is_system_role,
    )


@router.get(
    "",
    response_model=list[RoleRead],
    # dependencies=[Depends(require_permissions("role:read"))],
)
async def list_roles(service: RoleService = Depends(get_role_service)):
    return await service.get_roles()


@router.get(
    "/{role_id}",
    response_model=RoleRead,
    # dependencies=[Depends(require_permissions("role:read"))],
)
async def get_role_by_id(
        role_id: UUID,
        service: RoleService = Depends(get_role_service),
):
    return await service.get_role_by_id(role_id)


@router.put(
    "/{role_id}",
    response_model=RoleRead,
    # dependencies=[Depends(require_permissions("role:update"))],
)
async def update_role(
        role_id: UUID,
        data: RoleUpdate,
        service: RoleService = Depends(get_role_service),
):
    return await service.update_role(
        role_id=role_id,
        role_name=data.role_name,
        is_system_role=data.is_system_role,
    )


@router.delete(
    "/{role_id}",
    # dependencies=[Depends(require_permissions("role:delete"))],
)
async def delete_role(
        role_id: UUID,
        service: RoleService = Depends(get_role_service),
):
    await service.delete_role(role_id)
    return {"message": "Role deleted successfully"}
