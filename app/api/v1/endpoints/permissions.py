from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.services.permission_service import PermissionService
from app.schemas.permission_schema import (
    PermissionCreate,
    PermissionUpdate,
    PermissionRead,
    PermissionReadWithRoles,
    PaginatedPermission,
)

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


# CREATE
@router.post(
    "",
    response_model=PermissionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    payload: PermissionCreate,
    db: AsyncSession = Depends(get_async_session),
):
    service = PermissionService(db)
    return await service.create_permission(
        permission_name=payload.permission_name,
        role_names=payload.role_names,
    )


# LIST
@router.get(
    "",
    response_model=PaginatedPermission,
)
async def list_permissions(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
):
    service = PermissionService(db)
    return await service.get_all(search, page, size)


# UPDATE
@router.put(
    "/{permission_id}",
    response_model=PermissionReadWithRoles,
)
async def update_permission(
    permission_id: UUID,
    payload: PermissionUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    service = PermissionService(db)
    return await service.update_permission(
        permission_id=permission_id,
        permission_name=payload.permission_name,
        role_names=payload.role_names,
    )


# DELETE
@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = PermissionService(db)
    await service.delete_permission(permission_id)
