from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.schemas import UserLoginResponse, UserLoginRequest, ResponseModel
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_async_session)):
    return AuthService(db)


@router.post("/login", response_model=ResponseModel[UserLoginResponse])
async def user_login(
        payload: UserLoginRequest, service: AuthService = Depends(get_auth_service)
):
    user, access_token = await service.login(payload)
    return ResponseModel(
        data=UserLoginResponse(
            user=user,
            access_token=access_token,
        )
    )
