from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import pwd_context, create_access_token
from app.exceptions import AppException
from app.repositories import UserRepository
from app.schemas import ErrorCode, UserLoginRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def login(self, payload: UserLoginRequest):
        # VALIDATION IF USER EXISTING
        user = await self.repo.get_by_email(email=payload.email)

        if not user:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="User not found"
            )

        # VALIDATION PASSWORD
        validate_password = pwd_context.verify(payload.password, user.password)
        if not validate_password:
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_REQUIRED,
                message="Wrong password"
            )

        # CREATE ACCESS TOKEN
        access_token = create_access_token({"user_id": str(user.id)})
        return user, access_token
