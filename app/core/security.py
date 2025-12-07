from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_async_session
from app.exceptions import AppException
from app.schemas import ErrorCode
from app.models.user_model import User, RoleEnum
from app.models.user_model import StatusEnum


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


async def auth_require(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> User:

    if not credentials:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Authorization token is required",
        )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("user_id")
        if not user_id:
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_REQUIRED,
                message="Invalid token payload",
            )

        user = await db.get(User, UUID(user_id))
        if not user:
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_REQUIRED,
                message="User not found",
            )

        if user.status != StatusEnum.active:
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_REQUIRED,
                message="User is inactive",
            )

        return user

    except ExpiredSignatureError:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Access token has expired",
        )
    except JWTError:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Invalid access token",
        )


def check_roles(*allowed_roles: RoleEnum):
    async def role_checker(user: User = Depends(auth_require)):
        if user.role not in allowed_roles:
            raise AppException(
                status_code=403,
                code=ErrorCode.AUTH_FORBIDDEN,
                message="You don't have permission to access this resource",
            )
        return user

    return role_checker
