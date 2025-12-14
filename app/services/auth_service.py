from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import verify_password, create_access_token
from app.core.security import hash_password
from app.exceptions import AppException
from app.models import User
from app.repositories import UserRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.auth_schema import UserRegisterRequest, UserLoginRequest
from app.schemas.error_schema import ErrorCode


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    # ---------------------------------------------------------
    # TOKEN HELPER
    # ---------------------------------------------------------
    @staticmethod
    def create_token(user: User) -> str:
        payload = {
            "user_id": str(user.id),
            "email": user.email,
        }
        return create_access_token(payload)

    # ---------------------------------------------------------
    # REGISTER
    # ---------------------------------------------------------
    async def register(self, payload: UserRegisterRequest) -> User:
        # CHECK EMAIL
        if await self.user_repo.get_by_email(payload.email):
            raise AppException(
                status_code=400,
                code=ErrorCode.EMAIL_ALREADY_EXISTS,
                message="Email already registered",
            )

        # RESOLVE ROLE
        role = None
        if payload.role_id:
            role = await self.role_repo.get_by_id(payload.role_id)
        elif payload.role_name:
            role = await self.role_repo.get_by_name(payload.role_name)

        if not role:
            raise AppException(
                status_code=400,
                code=ErrorCode.ROLE_NOT_FOUND,
                message="Role not found",
            )

        # CREATE USER
        user = User(
            fullname=payload.fullname,
            email=payload.email,
            password=hash_password(payload.password),
            role_id=role.id,
            company_name=payload.company_name,
            avatar_initial=payload.avatar_initial,
            status=payload.status,
        )

        return await self.user_repo.create(user)

    # ---------------------------------------------------------
    # LOGIN
    # ---------------------------------------------------------
    async def login(self, payload: UserLoginRequest):
        user = await self.user_repo.get_by_email(payload.email)

        # INVALID CREDENTIALS (EMAIL / PASSWORD)
        if not user or not verify_password(payload.password, user.password):
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_INVALID_CREDENTIALS,
                message="Invalid email or password",
            )

        access_token = self.create_token(user)
        return user, access_token
