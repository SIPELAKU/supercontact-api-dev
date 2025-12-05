from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app.core import settings
from app.exceptions import AppException
from app.models import UserRole
from app.schemas import ErrorCode

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    data.update({"exp": expire})
    access_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token


def auth_require(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # CHECK CREDENTIALS
    if not credentials:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Authorization token is required"
        )

    try:
        access_token = credentials.credentials
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user = payload.get("user")
        if not user:
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_REQUIRED,
                message="Invalid token payload"
            )
        return {
            "id": UUID(user["id"]),
            "role": user["role"],
        }

    except ExpiredSignatureError:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Access token has expired"
        )
    except JWTError:
        raise AppException(
            status_code=401,
            code=ErrorCode.AUTH_REQUIRED,
            message="Invalid access token"
        )


def check_roles(*allowed_roles: UserRole):
    def depends_auth(user=Depends(auth_require)):
        if user["role"] not in allowed_roles:
            raise AppException(
                status_code=403,
                code=ErrorCode.FORBIDDEN,
                message="Forbidden"
            )
        return user

    return depends_auth
