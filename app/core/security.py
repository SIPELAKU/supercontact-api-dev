from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.exceptions import AppException
from app.models import UserRole, UserStatus
from app.models.user_model import User
from app.schemas import ErrorCode

ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db_session():
    from app.db import get_async_session

    async for session in get_async_session():
        yield session


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
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


async def auth_require(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    if not credentials:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Authorization token is required",
        )

    payload = decode_access_token(credentials.credentials)

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

    if user.status != UserStatus.ACTIVE:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="User is inactive",
        )

    return user


def check_roles(*allowed_roles: UserRole):
    async def depends_auth(user: User = Depends(auth_require)):
        if user.role not in allowed_roles:
            raise AppException(
                status_code=403,
                code=ErrorCode.FORBIDDEN,
                message="You don't have permission to access this resource",
            )
        return user

    return depends_auth
