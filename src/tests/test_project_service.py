import json


def create_user(client) -> int:
    payload = {
        "email": "owner@example.com",
        "name": "Owner",
        "password": "secret123",
    }
    resp = client.post("/auth/register", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 201
    data = resp.get_json()
    return data["id"]


def test_create_and_list_projects(client):
    owner_id = create_user(client)

    # Create project
    project_payload = {
        "owner_id": owner_id,
        "name": "My Project",
    }
    resp = client.post("/projects", data=json.dumps(project_payload), content_type="application/json")
    assert resp.status_code == 201
    project = resp.get_json()
    assert project["name"] == "My Project"
    assert project["owner"] == owner_id

    # List projects
    resp_list = client.get(f"/projects?owner_id={owner_id}&limit=10&offset=0")
    assert resp_list.status_code == 200
    list_data = resp_list.get_json()
    assert list_data["count"] >= 1
    assert any(p["id"] == project["id"] for p in list_data["items"])
