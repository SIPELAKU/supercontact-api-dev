from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel


class ChangePasswordSchema(SQLModel):
    current_password: str
    new_password: str
    confirm_password: str

class UserSecurityResponse(SQLModel):
    two_factor_enabled: bool

class UserDeviceResponse(SQLModel):
    id: UUID
    browser: str
    device: str
    location: Optional[str]
    last_activity: datetime
