from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import reset_token
from app.db import get_async_session
from app.schemas import (
    ResendOtpRequest,
    ResendOtpResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    ResponseModel,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
    VerifyOtpRequest,
    VerifyOtpResponse,
)
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_async_session)):
    return AuthService(db)


# USER REGISTER
@router.post("/register", response_model=ResponseModel[UserRegisterResponse])
async def user_register(
    payload: UserRegisterRequest, service: AuthService = Depends(get_auth_service)
):
    data = await service.register(payload)

    return ResponseModel(data=data)


# USER LOGIN
@router.post("/login", response_model=ResponseModel[UserLoginResponse])
async def user_login(
    payload: UserLoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    user, access_token = await service.login(
        payload=payload,
        request=request,
    )

    return ResponseModel(
        data=UserLoginResponse(
            user=user,
            access_token=access_token,
        )
    )


# RESEND USER OTP
@router.post("/otp/resend", response_model=ResponseModel[ResendOtpResponse])
async def resend_user_otp(
    payload: ResendOtpRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.resend_user_otp(payload=payload)
    return ResponseModel(
        data=ResendOtpResponse(
            email=payload.email, otp_type=payload.otp_type, valid=True
        )
    )


# VERIFY USER OTP
@router.post("/otp/verify", response_model=ResponseModel[VerifyOtpResponse])
async def verify_user_otp(
    payload: VerifyOtpRequest,
    service: AuthService = Depends(get_auth_service),
):
    data = await service.verify_user_otp(payload=payload)
    return ResponseModel(data=data)


@router.post("/reset-password", response_model=ResponseModel[ResetPasswordResponse])
async def reset_password(
    payload: ResetPasswordRequest,
    user_id: UUID = Depends(reset_token),
    service: AuthService = Depends(get_auth_service),
):
    data = await service.reset_password(user_id=user_id, payload=payload)
    return ResponseModel(data=data)
