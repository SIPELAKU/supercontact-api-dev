import pytest

from app.models import User, UserRole, UserStatus
from app.repositories import UserRepository
from app.schemas import UserGetQuery


@pytest.mark.asyncio
async def test_create_user(db_async_session):
    repo = UserRepository(db_async_session)

    user = User(
        fullname="John Doe",
        email="john@example.com",
        password="hashedpass",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )

    saved_user = await repo.create(user)

    assert saved_user.id is not None
    assert saved_user.email == "john@example.com"


@pytest.mark.asyncio
async def test_list_users_search_filter(db_async_session):
    repo = UserRepository(db_async_session)

    users_data = [
        ("John Doe", "john@example.com", UserRole.ADMIN, UserStatus.ACTIVE),
        ("Jane Smith", "jane@example.com", UserRole.TENANT_ADMIN, UserStatus.INACTIVE),
        ("Alice", "alice@example.com", UserRole.TENANT_ADMIN, UserStatus.ACTIVE),
    ]

    for fullname, email, role, status in users_data:
        await repo.create(
            User(
                fullname=fullname,
                email=email,
                password="pass",
                role=role,
                status=status,
            ),
        )

    users, total = await repo.list_users(query_params=UserGetQuery(search="Jane"))

    assert total == 1
    assert users[0].email == "jane@example.com"


@pytest.mark.asyncio
async def test_delete_user(db_async_session):
    repo = UserRepository(db_async_session)

    user = await repo.create(
        User(
            fullname="Test",
            email="test@example.com",
            password="pass",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        ),
    )

    await repo.delete(user)

    deleted = await repo.get_by_id(user.id)
    assert deleted is None
