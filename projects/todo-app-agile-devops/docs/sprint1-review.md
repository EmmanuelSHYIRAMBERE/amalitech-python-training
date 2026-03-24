Sprint 1 Review — To-Do Web Application

Overview

Sprint 1 focused on building the core functionality of the To-Do web application while establishing a DevOps pipeline. The goal was to deliver a working prototype with basic task management features and automated testing.

Objectives

- Implement task creation functionality
- Enable viewing of tasks
- Allow marking tasks as complete
- Set up CI/CD pipeline with automated testing

Features Delivered

1. Task Creation
   Users can create tasks through a POST API endpoint. Each task includes a title and completion status.

2. Task Listing
   Users can retrieve all tasks using a GET endpoint. Tasks are returned in JSON format.

3. Task Completion
   Users can mark tasks as complete using a PUT endpoint. The task status updates immediately.

4. Web Application Setup
   A Flask-based web server was implemented to handle API requests.

5. CI/CD Pipeline
   GitHub Actions was configured to automatically run tests on every push and pull request.

6. Testing Integration
   Basic unit tests were created and integrated into the CI pipeline to ensure code reliability.

Demo / Evidence

- Application runs locally via Flask server
- API endpoints tested successfully
- CI pipeline shows successful test runs

Example Endpoints

- GET / → confirms app is running
- POST /tasks → create task
- GET /tasks → list tasks
- PUT /tasks/{id} → mark complete

Conclusion

Sprint 1 successfully delivered a working backend for the To-Do application with core task management features and a functioning CI/CD pipeline. The system meets the acceptance criteria defined in the Sprint 0 backlog.
