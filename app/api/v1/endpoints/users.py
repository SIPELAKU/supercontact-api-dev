from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import check_roles
from app.db import get_async_session
from app.models import UserRole
from app.schemas import ResponseModel, UserListResponse
from app.services import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_async_session)):
    return UserService(db)


# GET ALL USERS
@router.get(
    "",
    dependencies=[Depends(check_roles(UserRole.ADMIN))],
    response_model=ResponseModel[UserListResponse]
)
async def get_all_users(service: UserService = Depends(get_user_service)):
    data = await service.find_all()
    return ResponseModel(data=UserListResponse(**data))
