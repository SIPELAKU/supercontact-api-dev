from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field
from app.models.department_enum import DepartmentEnum


# CREATE
class BranchCreate(BaseModel):
    department: DepartmentEnum
    branch: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Branch name",
    )


# UPDATE
class BranchUpdate(BaseModel):
    department: Optional[DepartmentEnum] = None
    branch: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Branch name",
    )


# READ
class BranchRead(BaseModel):
    id: UUID
    department: DepartmentEnum
    branch: str
