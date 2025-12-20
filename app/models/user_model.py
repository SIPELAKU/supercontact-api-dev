from datetime import datetime, timezone, timedelta
from enum import StrEnum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Text, String, Enum, Index, func, Boolean, text
from sqlmodel import SQLModel, Field, Relationship


class UserStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class UserPosition(StrEnum):
    BUSINESS_OWNER = "Business Owner"
    C_LEVEL = "C-Level"
    SENIOR_MANAGER = "Senior Manager"
    STAFF = "Staff"
    OTHER = "Lainnya"


class UserOTPType(StrEnum):
    VERIFICATION_EMAIL = "Verification Email"
    RESET_PASSWORD = "Reset Password"

    @property
    def purpose(self) -> str:
        return {
            UserOTPType.VERIFICATION_EMAIL: "verify your email address",
            UserOTPType.RESET_PASSWORD: "reset your password",
        }[self]


def utc_now():
    return datetime.now(timezone.utc)


def otp_expired_at():
    return datetime.now(timezone.utc) + timedelta(minutes=10)


class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    role_name: str = Field(sa_column=Column(String(20), nullable=False))
    permission_id: Optional[UUID] = Field(foreign_key="role_permissions.id")

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
    permission: Optional["RolePermission"] = Relationship(back_populates="roles")


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permissions"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    permission_name: str = Field(sa_column=Column(String(30), nullable=False))

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
    roles: List["UserRole"] = Relationship(back_populates="permission")


class User(SQLModel, table=True):
    __tablename__ = "users"
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fullname: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    phone: str = Field(sa_column=Column(String(255), nullable=False))
    company: str = Field(sa_column=Column(String(255), nullable=False))
    position: UserPosition = Field(
        sa_column=Column(
            Enum(
                UserPosition,
                name="user_position_enum",
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
                native_enum=False
            ),
            nullable=False,
        ),
    )
    password: str = Field(sa_column=Column(Text, nullable=False))

    avatar_initial: str = Field(sa_column=Column(String(2), nullable=False))
    is_verified: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default=text("false")))
    role: Optional[UUID] = Field(foreign_key="user_roles.id")
    status: Optional[UserStatus] = Field(
        default=UserStatus.ACTIVE,
        sa_column=Column(
            Enum(
                UserStatus,
                name="status_enum",
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
                native_enum=False
            ),
            nullable=False,
        ),
    )

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        )
    )
    leads: List["Lead"] = Relationship(back_populates="user")
    pipelines: List["Pipeline"] = Relationship(back_populates="user")
    contact_notes: List["ContactNote"] = Relationship(back_populates="user")
    contact_tasks: List["ContactTask"] = Relationship(back_populates="user")
    detail: List["UserDetail"] = Relationship(back_populates="user")
    mailings: List["Mailing"] = Relationship(back_populates="user")
    otps: List["UserOTP"] = Relationship(back_populates="user")
    notes: List["Note"] = Relationship(back_populates="user")
    device: List["UserDevice"] = Relationship(back_populates="user")
    # sender: List["ChatMessage"] = Relationship(back_populates="user")
    # receiver: List["ChatMessage"] = Relationship(back_populates="user")

    __table_args__ = (
        Index("idx_user_fullname", "fullname"),
        Index("idx_user_email", "email"),
    )


class UserOTP(SQLModel, table=True):
    __tablename__ = "user_otps"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(foreign_key="users.id")
    code: str = Field(sa_column=Column(String(6), nullable=False))
    otp_type: UserOTPType = Field(
        sa_column=Column(
            Enum(
                UserOTPType,
                name="user_otp_type_enum",
                values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
                native_enum=False
            ),
            nullable=False,
        ),
    )
    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now() + interval '10 minutes'")
        )
    )

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        )
    )
    user: "User" = Relationship(back_populates="otps")
