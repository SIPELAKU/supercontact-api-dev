from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import verify_password, create_access_token
from app.core.security import hash_password
from app.exceptions import AppException
from app.models import User
from app.repositories import UserRepository
from app.repository.role_repository import RoleRepository
from app.schemas.auth_schema import UserRegisterRequest, UserLoginRequest
from app.schemas.error_schema import ErrorCode


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.db = db

    @staticmethod
    def create_token(user: User) -> str:
        return create_access_token(
            {
                "user_id": str(user.id),
                "email": user.email,
            }
        )

    # REGISTER
    async def register(self, payload: UserRegisterRequest) -> User:
        # cek email
        if await self.user_repo.get_by_email(payload.email):
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Email already registered",
            )

        # ambil role
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

        # generate avatar initial otomatis
        avatar_initial = self._generate_avatar_initial(payload.fullname)

        user = User(
            fullname=payload.fullname,
            email=payload.email,
            phone=payload.phone,
            company=payload.company,
            position=payload.position,
            password=hash_password(payload.password),
            confirm_password=hash_password(payload.password),
            avatar_initial=avatar_initial,
            role_id=role.id,
            status=payload.status,
        )

        return await self.user_repo.create(user)

    # =========================
    # LOGIN
    # =========================
    async def login(self, payload: UserLoginRequest):
        user = await self.user_repo.get_by_email(payload.email)

        if not user:
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_REQUIRED,
                message="Invalid email or password",
            )

        if not verify_password(payload.password, user.password):
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_REQUIRED,
                message="Invalid email or password",
            )

        token = self.create_token(user)
        return user, token

    @staticmethod
    def _generate_avatar_initial(fullname: str) -> str:
        if not fullname:
            return ""
        parts = fullname.strip().split()
        if len(parts) == 1:
            return parts[0][0].upper()
        return (parts[0][0] + parts[-1][0]).upper()
