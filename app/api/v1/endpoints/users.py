from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db import get_async_session
from app.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
)
from app.services.user_service import UserService
from app.utils.permissions import require_permissions

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_async_session)) -> UserService:
    return UserService(db)


@router.post(
    "",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions("user:create"))],
)
async def create_user(
    data: UserCreateRequest,
    service: UserService = Depends(get_user_service),
):
    new_user = await service.create_user(data)
    return new_user


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
    return UserListResponse(total=len(users), items=users)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions("user:read"))],
)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions("user:update"))],
)
async def update_user(
    user_id: UUID,
    data: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
):
    updated = await service.update_user(user_id, data)
    return updated


@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_permissions("user:delete"))],
)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}
