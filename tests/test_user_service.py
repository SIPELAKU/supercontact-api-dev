import uuid
import pytest
from fastapi import HTTPException
from app.services.user_service import UserService
from app.models.user_model import RoleEnum, StatusEnum
from app.schemas.user_schema import UserCreate, UserUpdate


@pytest.fixture
def service():
    return UserService()


@pytest.mark.asyncio
async def test_create_user_success(db, service):
    user_data = UserCreate(
        fullname="John Doe",
        email="john@example.com",
        password="password123",
        role=RoleEnum.ADMIN,
        status=StatusEnum.active,
    )

    user = await service.create(db, user_data)

    assert user.id is not None
    assert user.email == "john@example.com"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(db, service):
    user_data = UserCreate(
        fullname="User1",
        email="dup@example.com",
        password="pass",
        role=RoleEnum.ADMIN,
        status=StatusEnum.active,
    )

    await service.create(db, user_data)

    with pytest.raises(HTTPException) as exc:
        await service.create(db, user_data)

    assert exc.value.status_code == 400
    assert "Email already registered" in exc.value.detail


@pytest.mark.asyncio
async def test_update_user_success(db, service):
    user_data = UserCreate(
        fullname="Alice",
        email="alice@example.com",
        password="pass",
        role=RoleEnum.TENANT_ADMIN,
        status=StatusEnum.active,
    )
    user = await service.create(db, user_data)

    updated_data = UserUpdate(
        fullname="Alice Doe",
        email="alice.doe@example.com",
        role=RoleEnum.ADMIN,
        status=StatusEnum.inactive,
    )

    updated_user = await service.update(db, user.id, updated_data)

    assert updated_user.fullname == "Alice Doe"
    assert updated_user.role == RoleEnum.ADMIN
    assert updated_user.status == StatusEnum.inactive


@pytest.mark.asyncio
async def test_update_user_not_found(db, service):
    updated_data = UserUpdate(
        fullname="Unknown",
        email="unknown@example.com",
        role=RoleEnum.ADMIN,
        status=StatusEnum.active,
    )

    with pytest.raises(HTTPException) as exc:
        await service.update(db, uuid.uuid4(), updated_data)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_success(db, service):
    user_data = UserCreate(
        fullname="To Delete",
        email="delete@example.com",
        password="pass",
        role=RoleEnum.ADMIN,
        status=StatusEnum.active,
    )
    user = await service.create(db, user_data)

    result = await service.delete(db, user.id)
    assert result["message"] == "User deleted successfully"

    deleted = await service.repo.get_by_id(db, user.id)
    assert deleted is None
