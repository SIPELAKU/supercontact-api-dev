def test_login_success(client, db_session):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin",
        "password": "admin"
    })

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["success"] == True
    assert "access_token" in response_json["data"]
    assert "user" in response_json["data"]


def test_login_user_not_found(client, db_session):
    response = client.post("/api/v1/auth/login", json={
        "email": "salah",
        "password": "admin"
    })

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "User not found"


def test_login_wrong_password(client, db_session):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin",
        "password": "salah"
    })

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Wrong password"
