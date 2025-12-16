from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    permission_name: str
    model_config = ConfigDict(from_attributes=True)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    permission_name: Optional[str] = None


class PermissionAssignRoles(BaseModel):
    role_ids: List[UUID]


class RoleMini(BaseModel):
    id: UUID
    role_name: str

    model_config = ConfigDict(from_attributes=True)


class PermissionRead(PermissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PermissionReadWithRoles(PermissionRead):
    roles: List[RoleMini]
