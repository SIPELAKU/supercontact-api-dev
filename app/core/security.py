from datetime import datetime, timedelta, timezone
from enum import StrEnum
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.exceptions import AppException
from app.models.user_model import User
from app.schemas import ErrorCode

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
access_token_scheme = HTTPBearer(scheme_name="AccessToken", auto_error=False)

reset_token_scheme = HTTPBearer(scheme_name="ResetPasswordToken", auto_error=False)

TOKEN_EXPIRE_MINUTES = 60


class TokenType(StrEnum):
    ACCESS_TOKEN = "access_token"
    RESET_PASSWORD = "reset_password"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_db_session():
    from app.db import get_async_session

    async for session in get_async_session():
        yield session


def create_token(
    data: dict, token_type: TokenType, expire_minutes: int = TOKEN_EXPIRE_MINUTES
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})

    token_key = settings.SECRET_KEY

    if token_type == token_type.RESET_PASSWORD:
        token_key = settings.RESET_PASSWORD_KEY

    return jwt.encode(
        to_encode,
        token_key,
        algorithm=settings.ALGORITHM,
    )


async def auth_require(
    credentials: HTTPAuthorizationCredentials = Depends(access_token_scheme),
    db: AsyncSession = Depends(get_db_session),
):
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


def check_roles(*allowed_roles: str):
    async def depends_auth(user: User = Depends(auth_require)):
        if user.role not in allowed_roles:
            raise AppException(
                status_code=403,
                code=ErrorCode.FORBIDDEN,
                message="You don't have permission to access this resource",
            )
        return user

    return depends_auth


async def reset_token(
    credentials: HTTPAuthorizationCredentials = Depends(reset_token_scheme),
    db: AsyncSession = Depends(get_db_session),
):
    if not credentials:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Reset token is required",
        )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.RESET_PASSWORD_KEY,
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
        return UUID(user_id)

    except ExpiredSignatureError:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Reset token has expired",
        )
    except JWTError:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Invalid reset token",
        )
