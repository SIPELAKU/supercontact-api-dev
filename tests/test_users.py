import pytest

user_prefix = "/api/v1/users"


@pytest.mark.asyncio
async def test_get_all_users(client, auth_token):
    response = await client.get(
        user_prefix,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert "users" in response_json["data"]
    assert "total" in response_json["data"]


@pytest.mark.asyncio
async def test_get_all_users_without_token(client):
    response = await client.get(user_prefix)

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Authorization token is required"


@pytest.mark.asyncio
async def test_get_all_users_wrong_token(client):
    response = await client.get(
        user_prefix,
        headers={"Authorization": f"Bearer Token Salah"}
    )

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Invalid access token"
