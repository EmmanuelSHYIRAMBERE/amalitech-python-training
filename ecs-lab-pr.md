feat: deploy containerized Java web app to ECS Fargate with CloudFormation GitSync and CodeDeploy blue/green CI/CD

## Module 4 — ECS CI/CD Lab

### What this PR adds
- Spring Boot Java web app serving a static page (full name + lab name), with Actuator `/health` and a small `/api/version` endpoint
- Multi-stage Dockerfile (Maven builder / Temurin JRE Alpine runtime) with non-root user and HEALTHCHECK
- Two CloudFormation templates provisioned via **CloudFormation Git sync** (no manual `aws cloudformation deploy` for infra changes):
  - `network.yaml` — multi-AZ VPC, public subnets (ALB) and private subnets (ECS tasks) with **zero NAT gateways** — egress via VPC endpoints only
  - `app-platform.yaml` — ECR repo, public ALB, ECS Fargate service (blue/green via CodeDeploy), target-tracking autoscaling, CodePipeline, EventBridge rule, all supporting IAM roles
- GitHub OIDC-based AWS authentication for image push — no AWS credentials stored in GitHub secrets
- IAM role `github-actions-ecs-lab-push` with least-privilege, per-repo ECR inline policy
- GitHub Actions workflow: builds the app image and pushes both an immutable `<student>_<app>-<sha>` tag and a floating `latest` tag on every push to `app/**`
- EventBridge rule detects ECR image pushes and triggers CodePipeline automatically
- CodePipeline: ECR image source + GitHub deploy-spec source → CodeBuild (repackages `appspec.yaml`/`taskdef.json` to the artifact root) → CodeDeploy blue/green deploy to ECS

### Architecture
```
GitHub Push (app/**)
      │
      ▼
GitHub Actions (OIDC) ──► AWS STS (short-lived token)
      │
      ▼
docker build & tag (SHA + latest) ──► Amazon ECR (eu-north-1)
      │
      ▼
ECR PUSH event ──► EventBridge Rule ──► CodePipeline
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼               
                        ECR Source    GitHub Source (appspec/taskdef)
                              │              │
                              └──────┬───────┘
                                     ▼
                          CodeBuild (repackage to artifact root)
                                     ▼
                          CodeDeploy — Blue/Green
                                     ▼
                    ECS Fargate Service (private subnets)
                                     ▲
                                     │
                        Public ALB (public subnets, 2 AZs)
                                     ▲
                                Internet

Infra (network.yaml, app-platform.yaml)
      │
      ▼
CloudFormation "Git sync" ──► auto-deploys on template push (no pipeline, no Actions)
```

### Networking
- VPC `10.2.0.0/16`, 2 AZs, public + private subnets
- **No NAT Gateway** — private-subnet ECS tasks reach ECR and CloudWatch Logs exclusively via VPC interface endpoints (`ecr.api`, `ecr.dkr`, `logs`) plus an S3 gateway endpoint for image layers
- Security groups: ALB (80 from internet) → ECS tasks (8080 from ALB only) → VPC endpoints (443 from ECS tasks only)

### Resources deployed
| Resource | Name |
|----------|------|
| CloudFormation Stack (network) | `emmanuel-ecs-lab-network` |
| CloudFormation Stack (platform) | `emmanuel-ecs-lab-platform` |
| VPC | `emmanuel-ecs-lab-vpc` (`10.2.0.0/16`) |
| ECR Repository | `emmanuel-ecs-lab-app` (immutable tags, with `latest` exclusion) |
| ECS Cluster | `emmanuel-ecs-lab-cluster` |
| ECS Service | `emmanuel-ecs-lab-service` (Fargate, CodeDeploy-controlled) |
| ALB | `emmanuel-ecs-lab-alb` |
| CodeDeploy Application | `emmanuel-ecs-lab-app` |
| CodePipeline | `emmanuel-ecs-lab-pipeline` |
| CodeBuild Project | `emmanuel-ecs-lab-repackage-deployspec` |
| EventBridge Rule | `emmanuel-ecs-lab-ecr-push-rule` |
| IAM Role (GitHub OIDC) | `github-actions-ecs-lab-push` |
| IAM Inline Policy | `ecs-lab-ecr-push-policy` |
| Image Tag (immutable) | `emmanuelshyirambere_ecslab-<sha>` |
| Image Tag (pipeline trigger) | `latest` |

### CI/CD Flow
Every push to `feat/ecs-lab-ecs-cicd` touching `module4/ecs-lab/app/**` triggers the workflow which:
1. Configures AWS credentials via OIDC (no stored secrets)
2. Logs in to Amazon ECR
3. Builds the multi-stage Docker image
4. Tags and pushes both `emmanuelshyirambere_ecslab-<sha>` (immutable, permanent history) and `latest` (mutable, watched by CodePipeline)

From there, entirely within AWS (no GitHub Actions involvement):
5. EventBridge detects the `latest` push and starts CodePipeline
6. CodePipeline pulls the new image plus `appspec.yaml`/`taskdef.json` from GitHub
7. CodeBuild copies the deploy-spec files to the artifact root
8. CodeDeploy registers a new task definition revision, deploys to the idle (green) target group, shifts ALB traffic, and drains the old (blue) tasks

### Autoscaling
- ECS service: min 1 / desired 1 / max 4 tasks
- Target-tracking policy on `ECSServiceAverageCPUUtilization` (~50% target)

### Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Static page — full name + lab name |
| `GET /actuator/health` | GET | Health check (used by ALB target group) |
| `GET /api/version` | GET | `{app, version, student}` JSON |

## Screenshots

### CloudFormation — Network Stack (Git sync enabled)
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### CloudFormation — Platform Stack Outputs (ALB DNS, ECR URI, Cluster/Service names)
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### ALB Target Group — Healthy Target
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### ECR Repository — Image Tags Pushed
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### GitHub Actions — Workflow Run Success
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### IAM Role — Trust Policy (OIDC)
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### IAM Role — Inline ECR Policy
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### CodePipeline — Successful Execution (Source → Build → Deploy)
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### CodeDeploy — Blue/Green Deployment Succeeded
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### Application Running via ALB (browser or curl output)
<img width="918" height="477" alt="screenshot-placeholder" src="" />

### GitHub Secrets — No AWS Credentials Stored
<img width="918" height="477" alt="screenshot-placeholder" src="" />
