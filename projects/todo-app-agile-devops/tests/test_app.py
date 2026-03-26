from src.app import app

# ── Sprint 1 tests ──────────────────────────────────────────

def test_home():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_create_task():
    client = app.test_client()
    response = client.post("/tasks", json={"title": "Test Task"})
    assert response.status_code == 200


def test_summary():
    client = app.test_client()
    client.post("/tasks", json={"title": "Task 1"})
    response = client.get("/summary")
    assert response.status_code == 200


# ── Sprint 2 tests ──────────────────────────────────────────

def test_complete_task_not_found():
    client = app.test_client()
    response = client.put("/tasks/9999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Task not found"


def test_delete_task():
    client = app.test_client()
    create = client.post("/tasks", json={"title": "To Delete"})
    task_id = create.get_json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task deleted"
