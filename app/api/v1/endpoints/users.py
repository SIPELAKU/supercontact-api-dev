from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_async_session
from app.models.user_model import User, UserStatus
from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserResponse,
    # UserListResponse,
)
from app.core.security import hash_password
from app.exceptions import AppException
from app.schemas import ErrorCode

router = APIRouter()


@router.post("", response_model=UserResponse)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_async_session)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar():
        raise AppException(
            status_code=400,
            code=ErrorCode.BAD_REQUEST,
            message="Email already registered",
        )

    new_user = User(
        fullname=data.fullname,
        email=data.email,
        password=hash_password(data.password),
        employee_id=data.employee_id,
        role_id=data.role_id,
        department_id=data.department_id,
        status=UserStatus.PENDING,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# LIST USERS
# @router.get("", response_model=UserListResponse)
# async def list_users(
#     search: str | None = None,
#     skip: int = 0,
#     limit: int = 10,
#     db: AsyncSession = Depends(get_async_session),
# ):
#     query = select(User)

#     if search:
#         query = query.where(User.fullname.ilike(f"%{search}%"))

#     query = query.offset(skip).limit(limit)
#     result = await db.execute(query)
#     users = result.scalars().all()

#     total = len(users)

#     return UserListResponse(data=users, total=total)


# GET USER DETAIL
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_detail(user_id: UUID, db: AsyncSession = Depends(get_async_session)):
    user = await db.get(User, user_id)
    if not user:
        raise AppException(
            status_code=404,
            code=ErrorCode.NOT_FOUND,
            message="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    user = await db.get(User, user_id)
    if not user:
        raise AppException(
            status_code=404,
            code=ErrorCode.NOT_FOUND,
            message="User not found",
        )

    if data.password:
        data.password = hash_password(data.password)

    data_dict = data.dict(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_async_session)):
    user = await db.get(User, user_id)
    if not user:
        raise AppException(
            status_code=404,
            code=ErrorCode.NOT_FOUND,
            message="User not found",
        )

    user.status = UserStatus.INACTIVE

    await db.commit()
    return {"message": "User has been deactivated"}
