import asyncio

from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.core import hash_password
from app.db import get_async_session
from app.models import UserStatus, UserRole, User, UserPosition


# fullname: str = Field(sa_column=Column(String(255), nullable=False))
#     email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
#     phone: str = Field(sa_column=Column(String(255), nullable=False))
#     company: str = Field(sa_column=Column(String(255), nullable=False))
#     position: UserPosition = Field(
#         sa_column=Column(
#             Enum(
#                 UserPosition,
#                 name="user_position_enum",
#                 values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
#                 native_enum=False
#             ),
#             nullable=False,
#         ),
#     )
#     password: str = Field(sa_column=Column(Text, nullable=False))
#
#     avatar_initial: str = Field(sa_column=Column(String(2), nullable=False))
#     is_verified: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default=text("false")))
#     role: Optional[UUID] = Field(foreign_key="user_roles.id")
#     status: Optional[UserStatus] = Field(
#         default=UserStatus.ACTIVE,
#         sa_column=Column(
#             Enum(
#                 UserStatus,
#                 name="status_enum",
#                 values_callable=lambda enum_cls: [enum.value for enum in enum_cls],
#                 native_enum=False
#             ),
#             nullable=False,
#         ),
#     )


async def seed_users():
    db_gen = get_async_session()
    db = await anext(db_gen)
    query = await db.scalars(select(UserRole))
    roles = query.all()
    user_seed = [
        {"fullname": "admin", "email": "admin@example.com", "password": hash_password("admin"), "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER, "is_verified": True},
        {"fullname": "admin2", "email": "admin2@example.com", "password": hash_password("admin"),
         "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER, "is_verified": True},
        {"fullname": "admin3", "email": "admin3@example.com", "password": hash_password("admin"),
         "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER, "is_verified": True},
        {"fullname": "admin4", "email": "admin4@example.com", "password": hash_password("admin"),
         "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER, "is_verified": True},
        {"fullname": "admin5", "email": "admin5@example.com", "password": hash_password("admin"),
         "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER, "is_verified": True},
    ]

    for user in user_seed:
        db_user = User(**user)
        db.add(db_user)

    try:
        await db.commit()
    except IntegrityError as e:
        print(e)
        print("Rollback")
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    print("Running database seed...")
    asyncio.run(seed_users())
    print("Seed completed!")
