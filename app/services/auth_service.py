import secrets
from datetime import timezone, datetime
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import hash_password, verify_password, create_token, TokenType
from app.exceptions import AppException
from app.models import User, UserOTP, UserOTPType
from app.repositories import UserRepository
from app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    ResetPasswordRequest,
    ResendOtpRequest,
    VerifyOtpRequest,
    VerifyOtpResponse,
    ErrorCode,
)
from app.utils import brevo_send_email


def generate_avatar_initial(fullname: str) -> str:
    parts = fullname.strip().split()

    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()

    return parts[0][0].upper()


def generate_6_digit_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    @staticmethod
    def create_access_token(user: User):
        data = {
            "user_id": str(user.id),
            "email": user.email,
        }
        return create_token(data, token_type=TokenType.ACCESS_TOKEN)

    async def create_and_send_user_otp(self, user: User, otp_type: UserOTPType):
        user_otp = await self.repo.create_user_otp(user_otp=UserOTP(
            user_id=user.id,
            code=generate_6_digit_code(),
            otp_type=otp_type
        ))

        payload = {
            "sender": {
                "email": "afifu5882@gmail.com",
                "name": "Supercontact App"
            },
            "to": [
                {"email": user.email, "name": user.fullname}
            ],
            "templateId": 10,
            "params": {
                "type": user_otp.otp_type,
                "fullname": user.fullname,
                "purpose": user_otp.otp_type.purpose,
                "otp": user_otp.code,
                "expires_at": 10
            }
        }
        await brevo_send_email(payload=payload)

    async def register(self, payload: UserRegisterRequest):
        user = await self.repo.get_by_email(email=payload.email)
        if user:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Email already registered"
            )
        if payload.password != payload.confirm_password:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Passwords don't match"
            )

        avatar_initial = generate_avatar_initial(payload.fullname)

        user = User(**payload.model_dump())
        user.password = hash_password(payload.password)
        user.avatar_initial = avatar_initial
        await self.repo.create(user)

        await self.create_and_send_user_otp(user=user, otp_type=UserOTPType.VERIFICATION_EMAIL)

    async def resend_user_otp(self, payload: ResendOtpRequest):
        user = await self.repo.get_by_email(email=payload.email)
        if not user:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="User not found"
            )
        if payload.otp_type == UserOTPType.VERIFICATION_EMAIL and user.is_verified:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="User already verified"
            )
        if payload.otp_type == UserOTPType.RESET_PASSWORD and not user.is_verified:
            await self.create_and_send_user_otp(user=user, otp_type=UserOTPType.VERIFICATION_EMAIL)
            raise AppException(
                status_code=400,
                code=ErrorCode.USER_NOT_VERIFIED,
                message="User not verified, check email for verification user"
            )

        active_count = await self.repo.count_user_otp_active(user_id=user.id)
        if active_count >= 3:
            raise AppException(
                status_code=429,
                code=ErrorCode.TOO_MANY_REQUESTS,
                message="Too many active OTP code. Please wait before requesting a new one."
            )

        await self.create_and_send_user_otp(user=user, otp_type=payload.otp_type)

    async def verify_user_otp(self, payload: VerifyOtpRequest):
        user = await self.repo.get_by_email(email=payload.email)
        if not user:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="User not found"
            )
        if payload.otp_type == UserOTPType.VERIFICATION_EMAIL and user.is_verified:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="User already verified"
            )

        user_otp = await self.repo.get_active_user_otp(user_id=user.id, otp_type=payload.otp_type)
        if not user_otp:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Verification code not found"
            )
        if payload.code != user_otp.code:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Invalid verification code"
            )
        now = datetime.now(timezone.utc)
        if user_otp.expires_at < now:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Verification code has expired"
            )

        # Invalidate OTP
        await self.repo.delete_all_user_otp(user_id=user.id, otp_type=payload.otp_type)

        # IF VERIFICATION EMAIL
        if payload.otp_type == UserOTPType.VERIFICATION_EMAIL:
            # Mark user as verified
            user.is_verified = True
            await self.repo.update(user)

            return VerifyOtpResponse(
                email=payload.email,
                otp_type=payload.otp_type,
                access_token=self.create_access_token(user=user),
                reset_token=None,
            )
        # IF RESET PASSWORD
        elif payload.otp_type == UserOTPType.RESET_PASSWORD:
            reset_token = create_token(
                {"user_id": str(user.id), "type": UserOTPType.RESET_PASSWORD},
                token_type=TokenType.RESET_PASSWORD,
                expire_minutes=10
            )
            return VerifyOtpResponse(
                email=user.email,
                otp_type=payload.otp_type,
                access_token=None,
                reset_token=reset_token,
            )

        return None

    async def login(self, payload: UserLoginRequest):
        user = await self.repo.get_by_email(email=payload.email)

        if not user:
            raise AppException(
                status_code=404, code=ErrorCode.NOT_FOUND, message="User not found"
            )

        validate_password = verify_password(payload.password, user.password)
        if not validate_password:
            raise AppException(
                status_code=401, code=ErrorCode.AUTH_REQUIRED, message="Wrong password"
            )

        access_token = self.create_access_token(user)
        return user, access_token

    async def reset_password(self, user_id: UUID, payload: ResetPasswordRequest):
        user = await self.repo.get_by_id(user_id=user_id)
        if not user:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="User not found"
            )
        user.password = hash_password(payload.password)
        await self.repo.update(user)
