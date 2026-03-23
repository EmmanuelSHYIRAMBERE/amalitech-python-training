from src.app import app

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