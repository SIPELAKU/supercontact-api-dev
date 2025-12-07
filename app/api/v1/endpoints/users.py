from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import check_roles
from app.db import get_async_session
from app.models import UserRole
from app.schemas import ResponseModel, UserGetQuery
from app.schemas.user_schema import PaginatedUserResponse
from app.services import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_async_session)):
    return UserService(db)


@router.get(
    "",
    dependencies=[Depends(check_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN))],
    response_model=ResponseModel[PaginatedUserResponse],
)
async def get_all_users(query_params: UserGetQuery = Depends(), service: UserService = Depends(get_user_service)):
    users = await service.find_all_users(query_params)
    return ResponseModel(data=users)
