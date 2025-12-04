def test_get_all_users(client, auth_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert "users" in response_json["data"]
    assert "total" in response_json["data"]


def test_get_all_users_without_token(client):
    response = client.get("/api/v1/users")

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Authorization token is required"


def test_get_all_users_wrong_token(client):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer Token Salah"}
    )

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Invalid access token"
