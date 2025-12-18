from typing import Optional

from fastapi import Request
from starlette.responses import JSONResponse

from app.schemas import ErrorResponse, ErrorCode, ResponseModel


class AppException(Exception):

    def __init__(
        self,
        *,
        status_code: int,
        code: ErrorCode,
        message: str,
        details: Optional[dict] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}

        super().__init__(message)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel(
            success=False,
            data=None,
            error=ErrorResponse(
                code=exc.code,
                message=exc.message,
                details=exc.details,
            ),
        ).model_dump(),
    )
