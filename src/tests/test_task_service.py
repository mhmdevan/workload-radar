import json


def create_user(client) -> int:
    payload = {
        "email": "owner2@example.com",
        "name": "Owner2",
        "password": "secret123",
    }
    resp = client.post("/auth/register", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 201
    data = resp.get_json()
    return data["id"]


def create_project(client, owner_id: int) -> int:
    payload = {
        "owner_id": owner_id,
        "name": "Tasks Project",
    }
    resp = client.post("/projects", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 201
    data = resp.get_json()
    return data["id"]


def test_create_and_update_task(client):
    owner_id = create_user(client)
    project_id = create_project(client, owner_id)

    task_payload = {
        "title": "First task",
        "description": "Important",
        "assignee_id": owner_id,
    }
    resp = client.post(
        f"/tasks/project/{project_id}",
        data=json.dumps(task_payload),
        content_type="application/json",
    )
    assert resp.status_code == 201
    task = resp.get_json()
    assert task["title"] == "First task"
    task_id = task["id"]

    # List tasks
    resp_list = client.get(f"/tasks/project/{project_id}?limit=10&offset=0")
    assert resp_list.status_code == 200
    data_list = resp_list.get_json()
    assert data_list["count"] >= 1
    assert any(t["id"] == task_id for t in data_list["items"])

    # Update status
    update_payload = {"status": "done"}
    resp_update = client.patch(
        f"/tasks/{task_id}/status",
        data=json.dumps(update_payload),
        content_type="application/json",
    )
    assert resp_update.status_code == 200
    updated = resp_update.get_json()
    assert updated["status"] == "done"
