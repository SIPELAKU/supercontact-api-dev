from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.department_enum import DepartmentEnum


class BranchCreate(BaseModel):
    department: DepartmentEnum = Field(...)
    name: str = Field(..., min_length=2, max_length=100)


class BranchUpdate(BaseModel):
    department: Optional[DepartmentEnum] = Field(None)
    name: Optional[str] = None


class BranchRead(BaseModel):
    id: UUID
    department: DepartmentEnum
    name: str

    model_config = ConfigDict(from_attributes=True)
