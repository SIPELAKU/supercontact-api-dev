from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.services.manage_user_service import ManageUserService
from app.schemas import (
    ManageUserCreateRequest,
    ManageUserUpdateRequest,
    ManageUserResponse,
    ManageUserListResponse,
)


router = APIRouter(
    prefix="/manage-users",
    tags=["Manage Users"],
)


@router.post(
    "",
    response_model=ManageUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_manage_user(
    payload: ManageUserCreateRequest,
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)
    return await service.create(payload)


@router.get(
    "/{id}",
    response_model=ManageUserResponse,
)
async def get_manage_user(
    id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)
    return await service.get_by_id(id)


@router.get(
    "",
    response_model=ManageUserListResponse,
)
async def list_manage_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)

    items = await service.list(skip=skip, limit=limit)

    return {
        "total": len(items),
        "items": items,
    }


@router.put(
    "/{id}",
    response_model=ManageUserResponse,
)
async def update_manage_user(
    id: UUID,
    payload: ManageUserUpdateRequest,
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)
    return await service.update(id, payload)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_manage_user(
    id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)
    await service.delete(id)
