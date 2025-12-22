from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
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

    model_config = ConfigDict(
        populate_by_name=True,
    )


# UPDATE
class BranchUpdate(BaseModel):
    department: Optional[DepartmentEnum] = None
    branch: Optional[str] = Field(
        None,
        description="Branch name",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


# READ
class BranchRead(BaseModel):
    id: UUID
    department: DepartmentEnum
    branch: str = Field(alias="name")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
