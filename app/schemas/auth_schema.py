from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import UserPosition


# ==================================================
# USER DTO (UNTUK RESPONSE)
# ==================================================
class UserResponse(BaseModel):
    id: UUID
    fullname: str
    email: EmailStr
    avatar_initial: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================================================
# REGISTER
# ==================================================
class UserRegisterRequest(BaseModel):
    fullname: str
    email: EmailStr
    phone: str
    company: str
    position: UserPosition

    password: str = Field(min_length=8, max_length=64)
    confirm_password: str = Field(min_length=8, max_length=64)

    # 🔐 bcrypt limit protection
    @field_validator("password")
    @classmethod
    def password_max_72_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password maksimal 72 byte")
        return v

    # 🔁 password confirmation
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if v != info.data.get("password"):
            raise ValueError("Password dan confirm password tidak sama")
        return v


class UserRegisterResponse(BaseModel):
    user: UserResponse

    model_config = {"from_attributes": True}


# ==================================================
# LOGIN
# ==================================================
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    user: UserResponse
    access_token: str

    model_config = {"from_attributes": True}


# ==================================================
# PASSWORD RESET
# ==================================================
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str = Field(min_length=8, max_length=64)
    token: str

    @field_validator("new_password")
    @classmethod
    def new_password_max_72_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password maksimal 72 byte")
        return v
