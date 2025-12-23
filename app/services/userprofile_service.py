from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.userprofile_repository import UserProfileRepository
from app.schemas.userprofile_schema import UserProfileResponse
from sqlalchemy import select
from app.models.userprofile_model import UserDetail


class UserProfileService:
    def __init__(self, repo: UserProfileRepository):
        self.repo = repo

    async def get_profile(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> UserProfileResponse | None:

        user = await self.repo.get_user(db, user_id)
        if not user:
            return None

        detail = await self.repo.get_user_detail(db, user_id)

        return UserProfileResponse(
            id=user.id,
            fullname=user.fullname,
            email=user.email,
            avatar_initial=user.avatar_initial,
            status=user.status.value if user.status else None,
            role=getattr(user, "role_name", None),
            joined_date=user.created_at,

            company=getattr(detail, "company", None),
            country=getattr(detail, "country", None),
            language=getattr(detail, "language", None),
            phone=getattr(detail, "phone", None),
            skype=getattr(detail, "skype", None),
            bio=getattr(detail, "bio", None),
        )


    async def update_profile(
        self,
        db: AsyncSession,
        user_id: UUID,
        payload: dict
    ) -> UserProfileResponse | None:

        user = await self.repo.get_user(db, user_id)
        if not user:
            return None

        result = await db.execute(
            select(UserDetail).where(UserDetail.user_id == user_id)
        )
        user_detail = result.scalar_one_or_none()

        if not user_detail:
            user_detail = UserDetail(
                user_id=user_id,
                fullname=user.fullname,
                email=user.email
            )
            db.add(user_detail)

        for field in [
            "company",
            "country",
            "language",
            "phone",
            "skype",
            "bio",
        ]:
            if field in payload:
                setattr(user_detail, field, payload[field])

        await db.commit()
        await db.refresh(user_detail)

        return await self.get_profile(db, user_id)


