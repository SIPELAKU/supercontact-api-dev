from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    role_name: str
    is_system_role: bool = False

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    is_system_role: Optional[bool] = None


class RoleRead(RoleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
