from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import verify_password, create_access_token
from app.exceptions import AppException
from app.models import User
from app.repositories import UserRepository
from app.schemas.auth_schema import UserRegisterRequest, UserLoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.error_schema import ErrorCode
from app.core.security import hash_password
from app.utils.user_agent import parse_user_agent
from app.utils.user_agent import parse_user_agent
from app.models.userdevice_model import UserDevice
from sqlalchemy import select
from datetime import datetime
from fastapi import Request


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    @staticmethod
    def create_token(user: User):
        data = {
            "user_id": str(user.id),
            "email": user.email,
        }
        return create_access_token(data)

    async def register(self, payload: UserRegisterRequest):
        user = await self.repo.get_by_email(email=payload.email)

        if user:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Email already registered"
            )

        def generate_avatar_initial(fullname: str) -> str:
            if not fullname:
                return ""

            parts = fullname.strip().split()

            if len(parts) >= 2:
                return (parts[0][0] + parts[-1][0]).upper()

            return parts[0][0].upper()

        avatar_initial = generate_avatar_initial(payload.fullname)

        user = User(
            fullname=payload.fullname,
            email=payload.email,
            phone=payload.phone,
            company=payload.company,
            position=payload.position,
            password=hash_password(payload.password),
            confirm_password=hash_password(payload.password),
            avatar_initial=avatar_initial,
        )
        return await self.repo.create(user)

    async def login(
        self,
        payload: UserLoginRequest,
        db: AsyncSession,
        request: Request,
    ):
        user = await self.repo.get_by_email(email=payload.email)

        if not user:
            raise AppException(...)

        if not verify_password(payload.password, user.password):
            raise AppException(...)

        browser, device = parse_user_agent(
            request.headers.get("user-agent", "")
        )

        result = await db.execute(
            select(UserDevice).where(
                UserDevice.user_id == user.id,
                UserDevice.browser == browser,
                UserDevice.device == device,
            )
        )
        user_device = result.scalar_one_or_none()

        if user_device:
            user_device.last_activity = datetime.utcnow()

        else:
            db.add(
                UserDevice(
                    user_id=user.id,
                    browser=browser,
                    device=device,
                )
            )

        await db.commit()

        access_token = self.create_token(user)
        return user, access_token

    async def forgot_password(self, payload: ForgotPasswordRequest):
        user = await self.repo.get_by_email(email=payload.email)
        if not user:
            raise AppException(
                status_code=404, code=ErrorCode.NOT_FOUND, message="User not found"
            )

        reset_token = create_access_token({"sub": str(user.id), "type": "reset"})
        return reset_token

    async def reset_password(self, payload: ResetPasswordRequest):
        user = await self.repo.get_by_email(payload.email)
        if not user:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="User not found"
            )

        user.password = hash_password(payload.new_password)
        await self.repo.commit()
        return "Password updated successfully"