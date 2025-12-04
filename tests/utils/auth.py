def authenticate_test_user(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin",
        "password": "admin"
    })

    assert response.status_code == 200
    return response.json()["data"]["access_token"]
