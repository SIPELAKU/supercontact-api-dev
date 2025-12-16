from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    ManageUserListResponse,
    ManagerDropdown,

)
from app.services import ManageUserService
from app.services import UserService

router = APIRouter(prefix="/manage-users", tags=["Manage Users"])


def get_user_service(
        db: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(db)


# CREATE USER
@router.post(
    "",
    response_model=UserResponse,
    # dependencies=[Depends(require_permissions("user:create"))],
)
async def create_user(
        data: UserCreateRequest,
        service: ManageUserService = Depends(get_user_service),
):
    return await service.create_user(data)


@router.get(
    "",
    response_model=ManageUserListResponse,
    # dependencies=[Depends(require_permissions("user:read"))],
)
async def list_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=200),
        service: UserService = Depends(get_user_service),
):
    users = await service.list_users(skip=skip, limit=limit)
    return ManageUserListResponse(
        total=len(users),
        items=users,
    )


@router.get(
    "/dropdown/managers",
    response_model=List[ManagerDropdown],
    # dependencies=[Depends(require_permissions("user:read"))],
)
async def manager_dropdown(
        service: UserService = Depends(get_user_service),
):
    """ """
    return await service.get_manager_dropdown()


# GET USER DETAIL
@router.get(
    "/{manage_user_id}",
    response_model=UserResponse,
    # dependencies=[Depends(require_permissions("user:read"))],
)
async def get_user(
        manage_user_id: UUID,
        service: UserService = Depends(get_user_service),
):
    return await service.get_user(manage_user_id)


# UPDATE USER
@router.put(
    "/{manage_user_id}",
    response_model=UserResponse,
    # dependencies=[Depends(require_permissions("user:update"))],
)
async def update_user(
        manage_user_id: UUID,
        data: UserUpdateRequest,
        service: UserService = Depends(get_user_service),
):
    return await service.update_user(manage_user_id, data)


# DELETE USER
@router.delete(
    "/{manage_user_id}",
    # dependencies=[Depends(require_permissions("user:delete"))],
)
async def delete_user(
        manage_user_id: UUID,
        service: UserService = Depends(get_user_service),
):
    await service.delete_user(manage_user_id)
    return {"message": "User deleted successfully"}
