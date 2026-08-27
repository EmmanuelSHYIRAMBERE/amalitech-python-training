# ECS Lab App

Minimal Spring Boot app for the ECS CI/CD lab. Serves a static page (full name + lab name) and exposes health/version endpoints used by the ALB and CodeDeploy blue/green checks.

## Endpoints

- `GET /` — static page
- `GET /actuator/health` — health check (used by the ALB target groups)
- `GET /api/version` — `{app, version, student}` JSON

## Local development

```bash
mvn spring-boot:run
```

## Docker

```bash
docker build -t ecs-lab-app .
docker run -p 8080:8080 ecs-lab-app
curl http://localhost:8080/
curl http://localhost:8080/actuator/health
```
