from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel


class UserProfileSchema(SQLModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    phone: Optional[str] = None
    skype: Optional[str] = None
    bio: Optional[str] = None


class UserProfileResponse(SQLModel):
    id: UUID
    fullname: str
    email: EmailStr
    avatar_initial: Optional[str]
    status: Optional[str]
    role: Optional[str]
    joined_date: datetime

    company: Optional[str]
    country: Optional[str]
    language: Optional[str]
    phone: Optional[str]
    skype: Optional[str]
    bio: Optional[str]

