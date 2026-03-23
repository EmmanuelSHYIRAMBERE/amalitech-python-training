from flask import Flask, request, jsonify

app = Flask(__name__)

tasks = []

@app.route("/")
def home():
    return "To-Do App Running"

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "completed": False
    }
    tasks.append(task)
    return jsonify(task)

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def complete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return jsonify(task)
    return {"error": "Task not found"}, 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return {"message": "Task deleted"}

@app.route("/summary", methods=["GET"])
def get_summary():
    completed = sum(1 for t in tasks if t["completed"])
    pending = sum(1 for t in tasks if not t["completed"])

    return {
        "completed": completed,
        "pending": pending
    }

if __name__ == "__main__":
    app.run(debug=True)