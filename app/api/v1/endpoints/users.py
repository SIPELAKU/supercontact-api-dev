from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import check_roles
from app.db.session import get_async_session
from app.models.user_model import RoleEnum
from app.schemas import ResponseModel, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_async_session)):
    return UserService(db)


@router.get(
    "",
    dependencies=[Depends(check_roles([RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN]))],
    response_model=ResponseModel[list[UserResponse]],
)
async def get_all_users(service: UserService = Depends(get_user_service)):
    users = await service.find_all()
    return ResponseModel(data=users)
