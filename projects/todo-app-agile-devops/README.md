# Todo App — Agile & DevOps Project

A simple Todo List web application built as part of an Agile & DevOps training project.  
This project demonstrates iterative development, testing, CI/CD pipelines, and basic logging/monitoring.

---

## 🏆 Project Overview

- **Objective:** Build a lightweight Todo app to manage tasks efficiently.
- **Tech Stack:** Python 3.14, OOP, Pytest, GitHub Actions CI/CD
- **Agile Focus:** Iterative delivery, backlog management, sprints
- **DevOps Focus:** CI/CD, unit testing, logging

---

## 🚀 Features

- Create new todo tasks
- Mark tasks as completed
- View all tasks
- Persist data (optional JSON storage)
- Logging of actions

---

---

## ⚡ Getting Started

### 1. Clone the repo

```bash
git clone <YOUR_REPO_URL>
cd todo-app-agile-devops
```

### 2. Create virtual environment & install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
poetry install
```

### 3. Run the application

```bash
python -m src.app
```

### 4. Run tests

```bash
pytest
```

Tests are integrated into GitHub Actions CI/CD workflow.

### CI/CD Pipeline

- GitHub Actions triggers on push or pull request
- Runs Pytest to ensure all tests pass
- Maintains clean commit history for iterative development

### Notes

- PYTHONPATH is set automatically in pytest.ini for correct imports
- Logging is implemented for monitoring actions
- The project follows Agile principles (Sprint 0–2) and DevOps best practices
