def test_read_root(client, hello):
    response = client.get("/")
    assert response.status_code == 200

    json = response.json()

    assert json["success"] is True
    assert json["data"]["message"] == "Server is running!"
    assert json["errors"] is None

    assert hello("world") == "Hello world"
