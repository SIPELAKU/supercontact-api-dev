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
from app.models.manage_user_model import UserStatus

router = APIRouter(prefix="/manage-users", tags=["Manage Users"])


# CREATE
@router.post(
    "",
    response_model=ManageUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_manage_user(
    payload: ManageUserCreateRequest,
    db: AsyncSession = Depends(get_async_session),
):
    return await ManageUserService(db).create(payload)


# LIST + SEARCH + FILTER
@router.get("", response_model=ManageUserListResponse)
async def list_manage_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[UserStatus] = Query(None),
    role_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    return await ManageUserService(db).list(
        page=page,
        limit=limit,
        search=search,
        status=status,
        role_id=role_id,
    )


# GET DETAIL
@router.get("/{id}", response_model=ManageUserResponse)
async def get_manage_user_detail(
    id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    return await ManageUserService(db).get_by_id(id)


# UPDATE
@router.put("/{id}", response_model=ManageUserResponse)
async def update_manage_user(
    id: UUID,
    payload: ManageUserUpdateRequest,
    db: AsyncSession = Depends(get_async_session),
):
    return await ManageUserService(db).update(id, payload)


# SOFT DELETE
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_manage_user(
    id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    await ManageUserService(db).deactivate(id)


# HARD DELETE
@router.delete(
    "/{id}/force",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def hard_delete_manage_user(
    id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    await ManageUserService(db).hard_delete(id)
