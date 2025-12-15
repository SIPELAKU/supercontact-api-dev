from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.userprofile_repository import UserProfileRepository
from app.schemas.userprofile_schema import AboutSchema
from sqlalchemy import select
from app.models.userprofile_model import UserDetail


class UserProfileService:
    def __init__(self, repo: UserProfileRepository):
        self.repo = repo

    async def get_profile(self, db: AsyncSession, user_id: UUID) -> dict:
        user = await self.repo.get_user(db, user_id)
        if not user:
            return None

        detail = await self.repo.get_user_detail(db, user_id)

        def to_dict(obj):
            if obj is None:
                return None
            if isinstance(obj, dict):
                return obj
            return {
                "country": getattr(obj, "country", None),
                "language": getattr(obj, "language", None),
                "phone": getattr(obj, "phone", None),
                "skype": getattr(obj, "skype", None),
                "bio": getattr(obj, "bio", None),
            }

        detail = to_dict(detail)

        profile = {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "avatar_initial": user.avatar_initial,
            "status": getattr(user.status, 'value', user.status) if user.status else None,
            "role": getattr(user, 'role_name', None),
            "joined_date": user.created_at,
            "about": AboutSchema(**detail) if detail else None,
        }

        return profile

    async def update_about(self, db: AsyncSession, user_id: UUID, payload: dict):
        result = await db.execute(
            select(UserDetail).where(UserDetail.user_id == user_id)
        )
        user_detail = result.scalar_one_or_none()

        if not user_detail:
            user_detail = UserDetail(user_id=user_id, **payload)
            db.add(user_detail)
        else:
            if "country" in payload:
                user_detail.country == payload["country"]
            if "language" in payload:
                user_detail.language == payload["language"]
            if "skype" in payload:
                user_detail.skype == payload["skype"]
            if "bio" in payload:
                user_detail.bio == payload["bio"]
            if "phone" in payload:
                user_detail.phone == payload["phone"]

        await db.commit()
        await db.refresh(user_detail)

        return user_detail

