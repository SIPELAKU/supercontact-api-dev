from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    PaginatedUserResponse,
    UserGetQuery,
)
from app.services import UserService
router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_async_session)):
    return UserService(db)


@router.post(
    "",
    response_model=UserResponse,
    # dependencies=[Depends(require_permissions("user:create"))],
)
async def create_user(
        data: UserCreateRequest,
        service: UserService = Depends(get_user_service),
):
    return await service.create(data)


@router.get(
    "",
    response_model=PaginatedUserResponse,
    # dependencies=[Depends(require_permissions("user:read"))],
)
async def list_users(
        query: UserGetQuery = Depends(),
        service: UserService = Depends(get_user_service),
):
    return await service.find_all_users(query)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    # dependencies=[Depends(require_permissions("user:read"))],
)
async def get_user(
        user_id: UUID,
        service: UserService = Depends(get_user_service),
):
    return await service.find_by_id(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    # dependencies=[Depends(require_permissions("user:update"))],
)
async def update_user(
        user_id: UUID,
        data: UserUpdateRequest,
        service: UserService = Depends(get_user_service),
):
    return await service.update(user_id, data)


@router.delete(
    "/{user_id}",
    # dependencies=[Depends(require_permissions("user:delete"))],
)
async def delete_user(
        user_id: UUID,
        service: UserService = Depends(get_user_service),
):
    return await service.delete(user_id)
