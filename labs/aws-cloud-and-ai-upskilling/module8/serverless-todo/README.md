# Serverless To-Do Lab (Module 8)

A fully serverless, Cognito-authenticated task management app. Users
sign up/sign in via Cognito; authenticated requests hit a Lambda-backed
REST API that reads/writes a DynamoDB table; tasks expire automatically
5 minutes after creation via a per-task EventBridge Scheduler schedule
unless completed or deleted first, in which case a DynamoDB Streams ->
SQS FIFO -> Lambda pipeline cancels the pending schedule. Expiry sends
an email via SNS, which every signed-in user is auto-subscribed to on
first login. The frontend is a build-free static site hosted on AWS
Amplify.

## Architecture

See `backend/infra/diagram/architecture.png` / `architecture.drawio`.

- **Auth**: Cognito User Pool, email+password, auto-confirmed sign-up
  (`PreSignUp` Lambda). `PostAuthentication` Lambda subscribes the
  user's email to a shared SNS topic.
- **API**: API Gateway REST API, Cognito authorizer, one Lambda
  (`tasks.py`) handling all CRUD routes.
- **Data**: DynamoDB, single-table design — `PK: UserId`, `SK: TaskId`
  (listing "my tasks" is a single `Query`, no GSI needed), on-demand
  billing, Streams enabled (`NEW_AND_OLD_IMAGES`).
- **Expiry workflow**: creating a task also creates a one-time
  EventBridge Scheduler schedule (named by `TaskId`) firing at
  `Deadline`. The `expiry` Lambda it invokes re-checks the task is
  still `Pending` (idempotent against a race with cancellation) before
  marking it `Expired` and publishing to SNS.
- **Cancellation workflow** (decoupled, per the spec's required shape):
  DynamoDB Streams → `stream_to_queue` Lambda (filtered to `REMOVE` and
  `MODIFY`-to-`Completed` events) → SQS FIFO queue (`MessageGroupId =
  TaskId`, content-based deduplication) → `cancellation` Lambda, which
  deletes the matching EventBridge schedule. Deleting an
  already-deleted schedule is treated as success, not an error — safe
  under SQS's at-least-once delivery.
- **Frontend**: plain HTML/CSS/vanilla JS (no build step) using
  `amazon-cognito-identity-js` (via CDN) for real Cognito SRP auth,
  hosted on Amplify. `amplify.yml`'s build step writes `config.js` from
  Amplify Console environment variables (`AWS_REGION`, `USER_POOL_ID`,
  `USER_POOL_CLIENT_ID`, `API_URL`) at build time.

## Deployment

### One-time manual prerequisites (CloudShell)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

for ENV in dev prod; do
  BUCKET="emmanuel-serverless-todo-sam-artifacts-${ENV}-${ACCOUNT_ID}"
  aws s3api create-bucket --bucket "$BUCKET" --region eu-north-1 \
    --create-bucket-configuration LocationConstraint=eu-north-1
  aws s3api put-bucket-versioning --bucket "$BUCKET" \
    --versioning-configuration Status=Enabled
  aws s3api put-public-access-block --bucket "$BUCKET" \
    --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
done
```

Then deploy the shared OIDC stack (`infra/github-oidc.yaml` at the repo
root) to create `github-actions-serverless-todo-push`, and add its ARN
as the `SERVERLESS_TODO_AWS_ROLE_ARN` GitHub secret.

### Automated backend deploys

- **dev**: `.github/workflows/serverless-todo-deploy-dev.yml` — auto,
  on push to `backend/**`.
- **prod**: `.github/workflows/serverless-todo-deploy-prod.yml` —
  fires only on a push to `backend/infra/.promote-to-prod`. To
  promote, edit that file and push.

### Frontend (Amplify)

1. In the Amplify Console, connect this repo, branch
   `feat/module8-serverless-todo`, base directory
   `labs/aws-cloud-and-ai-upskilling/module8/serverless-todo/frontend`.
2. Set environment variables (per branch/environment): `AWS_REGION`,
   `USER_POOL_ID`, `USER_POOL_CLIENT_ID`, `API_URL` — read these from
   the backend stack's outputs (`UserPoolId`, `UserPoolClientId`,
   `ApiUrl`) after a dev or prod deploy.
3. Amplify builds via `amplify.yml` (writes `config.js`, no bundler)
   and publishes the static site.

## Verification (live review)

- Sign up a new user → confirm no verification email/code is required
  (auto-confirmed) → sign in immediately.
- Create a task → confirm it appears under "Pending".
- Wait 5 minutes without completing it → confirm it moves to "Expired"
  and an email notification arrives (the address used to sign up).
- Create a second task, mark it "Completed" before 5 minutes elapse →
  confirm its EventBridge schedule is cancelled (no expiry email
  arrives, and `aws scheduler get-schedule` for that `TaskId` returns
  `ResourceNotFoundException`).
- Same check for deleting a task before its deadline.
