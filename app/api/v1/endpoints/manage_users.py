from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.db import get_async_session
from app.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
    ManagerDropdown,
)
from app.services.user_service import UserService
from app.utils.permissions import require_permissions

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(
    db: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(db)


# CREATE USER
@router.post(
    "",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions("user:create"))],
)
async def create_user(
    data: UserCreateRequest,
    service: UserService = Depends(get_user_service),
):
    """ """
    return await service.create_user(data)


@router.get(
    "",
    response_model=UserListResponse,
    dependencies=[Depends(require_permissions("user:read"))],
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    service: UserService = Depends(get_user_service),
):
    users = await service.list_users(skip=skip, limit=limit)
    return UserListResponse(
        total=len(users),
        items=users,
    )


@router.get(
    "/dropdown/managers",
    response_model=List[ManagerDropdown],
    dependencies=[Depends(require_permissions("user:read"))],
)
async def manager_dropdown(
    service: UserService = Depends(get_user_service),
):
    """ """
    return await service.get_manager_dropdown()


# GET USER DETAIL
@router.get(
    "/{id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions("user:read"))],
)
async def get_user(
    id: UUID,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user(id)


# UPDATE USER
@router.put(
    "/{id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions("user:update"))],
)
async def update_user(
    id: UUID,
    data: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(id, data)


# DELETE USER
@router.delete(
    "/{id}",
    dependencies=[Depends(require_permissions("user:delete"))],
)
async def delete_user(
    id: UUID,
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(id)
    return {"message": "User deleted successfully"}
