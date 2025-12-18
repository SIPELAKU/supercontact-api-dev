from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas import ResponseModel, UserLoginResponse, UserLoginRequest, VerifyOtpResponse, VerifyOtpRequest, \
    ResendOtpRequest, ResendOtpResponse
from app.schemas.auth_schema import UserRegisterResponse, UserRegisterRequest, ResetPasswordRequest, \
    ResetPasswordResponse
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_async_session)):
    return AuthService(db)


# USER REGISTER
@router.post("/register", response_model=ResponseModel[UserRegisterResponse])
async def user_register(payload: UserRegisterRequest, service: AuthService = Depends(get_auth_service)):
    await service.register(payload)

    return ResponseModel(
        data=UserRegisterResponse(
            message="Registration successful. Please check your email for the verification code."
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


# RESEND USER OTP
@router.post("/otp/resend", response_model=ResponseModel[ResendOtpResponse])
async def verify_user_otp(
        payload: ResendOtpRequest,
        service: AuthService = Depends(get_auth_service),
):
    await service.resend_user_otp(payload=payload)
    return ResponseModel(
        data=ResendOtpResponse(
            email=payload.email,
            otp_type=payload.otp_type,
            valid=True
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
        payload: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)
):
    message = await service.reset_password(payload)
    return ResponseModel(
        data=ResetPasswordResponse(message=message)
    )
