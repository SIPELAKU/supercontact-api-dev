from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel


class AboutSchema(SQLModel):
    country: Optional[str]
    language: Optional[str]
    phone: Optional[str]
    skype: Optional[str]
    bio: Optional[str]

class UserProfileResponse(SQLModel):
    id: UUID
    fullname: str
    email: EmailStr
    avatar_initial: Optional[str]
    status: Optional[str]
    role: Optional[str]
    joined_date: datetime

    about: Optional[AboutSchema] = None
