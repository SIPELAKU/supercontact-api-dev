from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import or_, func, delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserOTP
from app.models.user_model import User, UserOTPType
from app.schemas import UserGetQuery


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, query_params: UserGetQuery):
        query = select(User)

        if query_params.search:
            query = query.where(
                or_(
                    User.fullname.ilike(f"%{query_params.search}%"),
                    User.email.ilike(f"%{query_params.search}%"),
                )
            )

        # Pagination
        skip = (query_params.page - 1) * query_params.limit
        query = query.offset(skip).limit(query_params.limit)
        result = await self.db.scalars(query)
        users = result.all()

        # Count total rows
        total_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(total_query)

        return users, total

    async def get_by_email(self, email: EmailStr):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_id(self, user_id: UUID):
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User):
        await self.db.delete(user)
        await self.db.commit()

    async def get_all(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_total(self):
        return await self.db.scalar(select(func.count()).select_from(User))

    async def create_user_otp(self, user_otp: UserOTP):
        self.db.add(user_otp)
        await self.db.commit()
        return user_otp

    async def get_active_user_otp(self, user_id: UUID, otp_type: UserOTPType) -> UserOTP:
        query = (
            select(UserOTP)
            .where(UserOTP.user_id == user_id)
            .where(UserOTP.otp_type == otp_type)
            .order_by(UserOTP.created_at.desc())
        )

        return (await self.db.exec(query)).first()

    async def delete_all_user_otp(self, user_id: UUID, otp_type: UserOTPType):
        query = (
            delete(UserOTP)
            .where(UserOTP.user_id == user_id)
            .where(UserOTP.otp_type == otp_type)
        )

        await self.db.exec(query)
        await self.db.commit()
