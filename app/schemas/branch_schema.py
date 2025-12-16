from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import SQLModel, Field

if TYPE_CHECKING:
    from app.schemas.department_schema import DepartmentRead


class BranchBase(SQLModel):
    name: str
    department_id: UUID


class BranchCreate(BranchBase):
    pass


class BranchUpdate(SQLModel):
    name: Optional[str] = None
    department_id: Optional[UUID] = None


class BranchRead(BranchBase):
    id: UUID


class BranchReadWithDepartment(BranchRead):
    department: Optional["DepartmentRead"] = None


BranchReadWithDepartment.update_forward_refs()
