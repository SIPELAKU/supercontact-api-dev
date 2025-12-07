async def authenticate_test_user(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "admin"
    })

    assert response.status_code == 200
    result = response.json()

    return result["data"]["access_token"]
