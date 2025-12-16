from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.models.department_model import DepartmentName


class DepartmentBase(BaseModel):
    name: DepartmentName
    manager_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class DepartmentCreate(DepartmentBase):
    branches: List[str] = Field(
        default_factory=list, description="List nama branch yang akan dibuat langsung"
    )


class DepartmentUpdate(BaseModel):
    name: Optional[DepartmentName] = None
    manager_id: Optional[UUID] = None

    branches: Optional[List[str]] = Field(
        default=None, description="List branch baru (optional)"
    )

    model_config = ConfigDict(from_attributes=True)


class BranchReadSimple(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class DepartmentRead(DepartmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class DepartmentReadWithRelations(DepartmentRead):
    branches: List[BranchReadSimple] = []
