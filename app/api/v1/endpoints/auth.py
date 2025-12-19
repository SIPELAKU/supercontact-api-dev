from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas import ResponseModel, UserLoginResponse, UserLoginRequest
from app.schemas.auth_schema import UserRegisterResponse, UserRegisterRequest, ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse
from app.services import AuthService
from fastapi import Request

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

@router.post("/login", response_model=ResponseModel[UserLoginResponse])
async def user_login(
    payload: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    service: AuthService = Depends(get_auth_service),
):
    user, access_token = await service.login(
        payload=payload,
        db=db,
        request=request,
    )

    return ResponseModel(
        data=UserLoginResponse(
            user=user,
            access_token=access_token,
        )
    )

# USER FORGOT PASSWORD
@router.post("/forgot-password", response_model=ResponseModel[ForgotPasswordResponse])
async def forgot(
        payload: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)
):
    reset_token = await service.forgot_password(payload)
    return ResponseModel(
        data=ForgotPasswordResponse(reset_token=reset_token)
    )

@router.post("/reset-password", response_model=ResponseModel[ResetPasswordResponse])
async def reset(
        payload: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)
):
    message = await service.reset_password(payload)
    return ResponseModel(
        data=ResetPasswordResponse(message=message)
    )

