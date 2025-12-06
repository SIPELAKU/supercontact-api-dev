from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app.core import settings
from app.exceptions import AppException
from app.schemas import ErrorCode
from fastapi.responses import JSONResponse
from app.models.user_model import User
from app.db.session import get_async_session
from app.db.session import get_async_session

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
        user_id = payload.get("user_id")
        if not user_id:
            raise AppException(
                status_code=401,
                code=ErrorCode.AUTH_REQUIRED,
                message="Invalid token payload"
            )
        return UUID(user_id)

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

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(pwd_context),
    db: AsyncSession = Depends(get_async_session),
):
    #
    if isinstance(credentials, JSONResponse):
        return credentials

    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            return JSONResponse(
                status_code=401,
                content={
                    "status": "error",
                    "message": "Unauthorized",
                    "code": 401
                }
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(
                status_code=401,
                content={
                    "status": "error",
                    "message": "Unauthorized",
                    "code": 401
                }
            )

        return user

    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "message": "Unauthorized",
                "code": 401
            }
        )
    except Exception:
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "message": "Unauthorized",
                "code": 401
            }
        )

def hash_password(password: str) -> str:
    return pwd_context.hash(password)