from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.services.manage_user_service import ManageUserService
from app.schemas.manage_user_schema import (
    ManageUserCreateRequest,
    ManageUserUpdateRequest,
    ManageUserResponse,
    ManageUserListResponse,
)

router = APIRouter(
    prefix="/manage-users",
    tags=["Manage Users"],
)


# ==================================================
# CREATE
# ==================================================
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


# ==================================================
# LIST (PAGINATION + SEARCH + FILTER)
# ==================================================
@router.get(
    "",
    response_model=ManageUserListResponse,
)
async def list_manage_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    department: Optional[str] = None,
    branch: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)

    items = await service.get_all(
        page=page,
        limit=limit,
        search=search,
        role=role,
        department=department,
        branch=branch,
        status=status,
    )

    # NOTE:
    # total di sini adalah jumlah hasil query saat ini
    # (jika mau total seluruh data tanpa pagination,
    # kita bisa buat service count terpisah)
    return ManageUserListResponse(
        total=len(items),
        items=items,
    )


# ==================================================
# GET BY ID
# ==================================================
@router.get(
    "/{id}",
    response_model=ManageUserResponse,
)
async def get_manage_user_detail(
    id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)
    return await service.get_by_id(id)


# ==================================================
# UPDATE
# ==================================================
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


# ==================================================
# SOFT DELETE (SET STATUS = INACTIVE)
# ==================================================
@router.delete(
    "/{id}",
    response_model=ManageUserResponse,
)
async def soft_delete_manage_user(
    id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)
    return await service.soft_delete(id)


# ==================================================
# HARD DELETE (PERMANENT)
# ==================================================
@router.delete(
    "/{id}/force",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def hard_delete_manage_user(
    id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = ManageUserService(db)
    await service.hard_delete(id)
    return None
