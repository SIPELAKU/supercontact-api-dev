import pytest

auth_prefix = "/api/v1/auth"


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post(f"{auth_prefix}/login", json={
        "email": "admin@example.com",
        "password": "admin"
    })

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["success"] == True
    assert "access_token" in response_json["data"]
    assert "user" in response_json["data"]


@pytest.mark.asyncio
async def test_login_user_not_found(client):
    response = await client.post(f"{auth_prefix}/login", json={
        "email": "salah@example.com",
        "password": "admin"
    })

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "User not found"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    response = await client.post(f"{auth_prefix}/login", json={
        "email": "admin@example.com",
        "password": "salah"
    })

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Wrong password"
