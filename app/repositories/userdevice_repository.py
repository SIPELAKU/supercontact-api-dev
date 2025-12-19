from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, UserDevice
from app.utils import parse_user_agent


class UserDeviceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_update_device(self, request: Request, user: User):
        browser, device = parse_user_agent(
            request.headers.get("user-agent", "")
        )

        query = select(UserDevice).where(
            UserDevice.user_id == user.id,
            UserDevice.browser == browser,
            UserDevice.device == device,
        )

        result = await self.db.scalars(query)
        user_device = result.one_or_none()

        now = datetime.now(timezone.utc)

        if user_device:
            user_device.last_activity = now

        else:
            user_device = UserDevice(
                user_id=user.id,
                browser=browser,
                device=device,
                last_activity=datetime.now(timezone.utc),
            )
            self.db.add(user_device)

        await self.db.commit()
