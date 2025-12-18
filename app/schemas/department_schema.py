from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    branches: List[str] = Field(default_factory=list)


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    branches: Optional[List[str]] = None


class BranchReadSimple(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class DepartmentRead(DepartmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentReadWithRelations(DepartmentRead):
    branches: List[BranchReadSimple] = Field(default_factory=list)
