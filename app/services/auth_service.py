from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import verify_password, create_access_token
from app.exceptions import AppException
from app.models import User
from app.repositories import UserRepository
from app.schemas.auth_schema import UserRegisterRequest, UserLoginRequest
from app.schemas.error_schema import ErrorCode
from app.core.security import hash_password


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
            if len(parts) == 1:
                return parts[0][0].upper()
            return (parts[0][0] + parts[-1][0]).upper()

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

        access_token = self.create_token(user)
        return user, access_token
