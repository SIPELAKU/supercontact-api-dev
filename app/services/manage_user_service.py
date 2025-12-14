from typing import List, Optional
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models.user_model import User
from app.models.role_model import Role
from app.models.department_model import Department
from app.models.branch_model import Branch
from app.schemas.user_schema import UserCreateRequest, UserUpdateRequest
from app.core.security import hash_password
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_role_by_name(self, role_name: str) -> Role:
        result = await self.db.execute(select(Role).where(Role.role_name == role_name))
        role = result.scalars().first()
        if not role:
            raise AppException(ErrorCode.ROLE_NOT_FOUND, "Role not found")
        return role

    async def _get_department_by_name(
        self, department_name: Optional[str]
    ) -> Optional[Department]:
        if not department_name:
            return None

        result = await self.db.execute(
            select(Department).where(Department.name == department_name)
        )
        department = result.scalars().first()
        if not department:
            raise AppException(ErrorCode.DEPARTMENT_NOT_FOUND, "Department not found")
        return department

    async def _get_branch_by_name(self, branch_name: Optional[str]) -> Optional[Branch]:
        if not branch_name:
            return None

        result = await self.db.execute(select(Branch).where(Branch.name == branch_name))
        branch = result.scalars().first()
        if not branch:
            raise AppException(ErrorCode.BRANCH_NOT_FOUND, "Branch not found")
        return branch

    async def _validate_branch_belongs_to_department(
        self,
        branch: Optional[Branch],
        department: Optional[Department],
    ):
        if not branch or not department:
            return

        if branch.department_id != department.id:
            raise AppException(
                ErrorCode.BRANCH_NOT_IN_DEPARTMENT,
                "Branch does not belong to the selected department",
            )

    async def _check_unique_email(
        self, email: str, exclude_user_id: Optional[UUID] = None
    ):
        query = select(User).where(User.email == email)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)

        result = await self.db.execute(query)
        if result.scalars().first():
            raise AppException(
                status_code=400,
                code=ErrorCode.USER_EMAIL_EXISTS,
                message="Email already used",
            )

    async def _check_unique_employee_id(
        self, employee_id: Optional[str], exclude_user_id: Optional[UUID] = None
    ):
        if not employee_id:
            return

        query = select(User).where(User.employee_id == employee_id)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)

        result = await self.db.execute(query)
        if result.scalars().first():
            raise AppException(
                ErrorCode.USER_EMPLOYEE_ID_EXISTS, "Employee ID already used"
            )

    async def create_user(self, data: UserCreateRequest) -> User:
        await self._check_unique_email(data.email)
        await self._check_unique_employee_id(data.employee_id)

        role = await self._get_role_by_name(data.role)
        department = await self._get_department_by_name(data.department)
        branch = await self._get_branch_by_name(data.branch)

        await self._validate_branch_belongs_to_department(branch, department)

        new_user = User(
            fullname=data.fullname,
            email=data.email,
            password=hash_password(data.password),
            role_id=role.id,
            department_id=department.id if department else None,
            branch_id=branch.id if branch else None,
            user_level=data.user_level,
            employee_id=data.employee_id,
            status=data.status,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user(self, user_id: UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise AppException(ErrorCode.USER_NOT_FOUND, "User not found")
        return user

    async def list_users(self, skip: int = 0, limit: int = 20) -> List[User]:
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update_user(self, user_id: UUID, data: UserUpdateRequest) -> User:
        user = await self.get_user(user_id)

        if data.email and data.email != user.email:
            await self._check_unique_email(data.email, user.id)

        if data.employee_id and data.employee_id != user.employee_id:
            await self._check_unique_employee_id(data.employee_id, user.id)

        role = await self._get_role_by_name(data.role) if data.role else None

        department = (
            await self._get_department_by_name(data.department)
            if data.department
            else None
        )

        branch = await self._get_branch_by_name(data.branch) if data.branch else None

        await self._validate_branch_belongs_to_department(
            branch or None,
            department or None,
        )

        if data.fullname is not None:
            user.fullname = data.fullname
        if data.email is not None:
            user.email = data.email
        if role:
            user.role_id = role.id
        if department is not None:
            user.department_id = department.id
        if branch is not None:
            user.branch_id = branch.id
        if data.user_level is not None:
            user.user_level = data.user_level
        if data.employee_id is not None:
            user.employee_id = data.employee_id
        if data.status is not None:
            user.status = data.status
        if data.password:
            user.password = hash_password(data.password)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID):
        user = await self.get_user(user_id)
        await self.db.delete(user)
        await self.db.commit()
