from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class ErrorCode(StrEnum):
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"  # Validasi data request salah
    AUTH_REQUIRED = "AUTH_REQUIRED"  # Token tidak ditemukan
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    USER_EMPLOYEE_ID_EXISTS = "USER_EMPLOYEE_ID_EXISTS"
    ROLE_NOT_FOUND = "ROLE_NOT_FOUND"
    FORBIDDEN = "FORBIDDEN"  # Role tidak cukup
    NOT_FOUND = "NOT_FOUND"  # Data tidak ditemukan
    INTEGRATION_ERROR = "INTEGRATION_ERROR"  # Error komunikasi dengan Odoo
    SERVER_ERROR = "SERVER_ERROR"  # Unexpected


class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str
    details: Optional[dict] = None
