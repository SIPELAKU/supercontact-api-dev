import uuid

import pytest

from app.exceptions import AppException
from app.models import UserRole, UserStatus
from app.schemas import UserCreateRequest, UserUpdateRequest
from app.services import UserService


@pytest.fixture
def service(db_async_session):
    return UserService(db_async_session)


@pytest.mark.asyncio
async def test_create_user_success(service):
    user_data = UserCreateRequest(
        fullname="John Doe",
        email="john@example.com",
        password="password123",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )

    user = await service.create(user_data)

    assert user.id is not None
    assert user.email == "john@example.com"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(service):
    user_data = UserCreateRequest(
        fullname="User1",
        email="dup@example.com",
        password="pass",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )

    await service.create(user_data)

    user_data1 = UserCreateRequest(
        fullname="User1",
        email="dup@example.com",
        password="pass",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )

    with pytest.raises(AppException) as exc:
        await service.create(user_data1)

    assert exc.value.status_code == 400
    assert "Email already registered" in exc.value.message


@pytest.mark.asyncio
async def test_update_user_success(service):
    user_data = UserCreateRequest(
        fullname="Alice",
        email="alice@example.com",
        password="pass",
        role=UserRole.TENANT_ADMIN,
        status=UserStatus.ACTIVE,
    )
    user = await service.create(user_data)

    updated_data = UserUpdateRequest(
        fullname="Alice Doe",
        email="alice.doe@example.com",
        role=UserRole.ADMIN,
        status=UserStatus.INACTIVE,
    )

    updated_user = await service.update(user.id, updated_data)

    assert updated_user.fullname == "Alice Doe"
    assert updated_user.role == UserRole.ADMIN
    assert updated_user.status == UserStatus.INACTIVE


@pytest.mark.asyncio
async def test_update_user_not_found(service):
    updated_data = UserUpdateRequest(
        fullname="Unknown",
        email="unknown@example.com",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )

    with pytest.raises(AppException) as exc:
        await service.update(uuid.uuid4(), updated_data)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_success(service):
    user_data = UserCreateRequest(
        fullname="To Delete",
        email="delete@example.com",
        password="pass",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    user = await service.create(user_data)

    result = await service.delete(user.id)
    assert result["message"] == "User deleted successfully"

    deleted = await service.repo.get_by_id(user.id)
    assert deleted is None
