from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas import ResponseModel, UserLoginResponse, UserLoginRequest
from app.schemas.auth_schema import UserRegisterResponse, UserRegisterRequest
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_async_session)):
    return AuthService(db)


# USER REGISTER
@router.post("/register", response_model=ResponseModel[UserRegisterResponse])
async def user_register(payload: UserRegisterRequest, service: AuthService = Depends(get_auth_service)):
    user = await service.register(payload)

    return ResponseModel(
        data=UserRegisterResponse(
            user=user
        )
    )


# USER LOGIN
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
