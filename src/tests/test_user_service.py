import json


def test_user_registration_and_login(client):
    payload = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "secret123",
    }

    # Register
    resp = client.post("/auth/register", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert "id" in data

    # Login
    login_payload = {"email": payload["email"], "password": payload["password"]}
    resp_login = client.post("/auth/login", data=json.dumps(login_payload), content_type="application/json")
    assert resp_login.status_code == 200
    login_data = resp_login.get_json()
    assert "token" in login_data
    assert login_data["user"]["email"] == payload["email"]
