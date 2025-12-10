from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel


class PermissionCreate(BaseModel):
    name: str


class RoleCreate(BaseModel):
    name: str
    permissions: Optional[List[UUID]] = None


class RoleResponse(BaseModel):
    id: UUID
    name: str
    is_system_role: bool
    permissions: List[PermissionResponse]

    model_config = {"from_attributes": True}


class PermissionResponse(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class RoleListResponse(BaseModel):
    total: int
    page: int
    total_pages: int
    roles: List[RoleResponse]
