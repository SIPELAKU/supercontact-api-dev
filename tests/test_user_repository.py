import pytest
from app.repository.user_repository import UserRepository
from app.models.user_model import User, RoleEnum, StatusEnum


@pytest.mark.asyncio
async def test_create_user(db):
    repo = UserRepository()

    user = User(
        fullname="John Doe",
        email="john@example.com",
        password="hashedpass",
        role=RoleEnum.ADMIN,
        status=StatusEnum.active,
    )

    saved_user = await repo.create(db, user)

    assert saved_user.id is not None
    assert saved_user.email == "john@example.com"


@pytest.mark.asyncio
async def test_list_users_search_filter(db):
    repo = UserRepository()

    users_data = [
        ("John Doe", "john@example.com", RoleEnum.ADMIN, StatusEnum.active),
        ("Jane Smith", "jane@example.com", RoleEnum.TENANT_ADMIN, StatusEnum.inactive),
        ("Alice", "alice@example.com", RoleEnum.TENANT_ADMIN, StatusEnum.active),
    ]

    for fullname, email, role, status in users_data:
        await repo.create(
            db,
            User(
                fullname=fullname,
                email=email,
                password="pass",
                role=role,
                status=status,
            ),
        )

    users, total = await repo.list_users(db, "Jane", None, None, 0, 10)

    assert total == 1
    assert users[0].email == "jane@example.com"


@pytest.mark.asyncio
async def test_delete_user(db):
    repo = UserRepository()

    user = await repo.create(
        db,
        User(
            fullname="Test",
            email="test@example.com",
            password="pass",
            role=RoleEnum.ADMIN,
            status=StatusEnum.active,
        ),
    )

    await repo.delete(db, user)

    deleted = await repo.get_by_id(db, user.id)
    assert deleted is None
