from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.department_schema import DepartmentRead


class BranchBase(BaseModel):
    name: str


class BranchCreate(BranchBase):
    department_id: UUID = Field(...)


class BranchUpdate(BaseModel):
    name: Optional[str] = None


class BranchRead(BranchBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class BranchReadWithDepartment(BranchRead):
    department: Optional[DepartmentRead] = None
