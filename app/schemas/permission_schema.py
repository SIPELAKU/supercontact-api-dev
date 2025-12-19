from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PermissionBase(BaseModel):
    permission_name: str
    model_config = ConfigDict(from_attributes=True)


# CREATE
class PermissionCreate(PermissionBase):
    role_names: Optional[List[str]] = Field(
        default=None,
        description="Assign permission to existing roles by role_name",
        example=["Admin", "Manager"],
    )


# UPDATE
class PermissionUpdate(BaseModel):
    permission_name: Optional[str] = None
    role_names: Optional[List[str]] = Field(
        default=None,
        description="Overwrite role access by role_name",
        example=["Admin", "Manager"],
    )


# ASSIGN
class PermissionAssignRoles(BaseModel):
    role_ids: List[UUID]


class PermissionAssignRolesByName(BaseModel):
    role_names: List[str]


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
