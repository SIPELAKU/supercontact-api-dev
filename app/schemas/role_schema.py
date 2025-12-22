from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# =========================
# CREATE (Swagger Input)
# =========================
class RoleCreate(BaseModel):
    role_name: str

    model_config = ConfigDict(from_attributes=True)


# READ
class RoleRead(BaseModel):
    id: UUID
    role_name: str
    is_system_role: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
