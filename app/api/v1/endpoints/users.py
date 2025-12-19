from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth_require
from app.db import get_async_session
from app.schemas import ResponseModel, UserGetQuery
from app.schemas.user_schema import PaginatedUserResponse
from app.services import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_async_session)):
    return UserService(db)


@router.get(
    "",
    dependencies=[Depends(auth_require)],
    response_model=ResponseModel[PaginatedUserResponse],
)
async def get_all_users(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        search: Optional[str] = Query(None),
        service: UserService = Depends(get_user_service)
):
    query_params = UserGetQuery(
        page=page,
        limit=limit,
        search=search,
    )
    users = await service.find_all_users(query_params=query_params)
    return ResponseModel(data=users)
