# Orders DynamoDB Lab (Module 7)

Deploys a single DynamoDB table (`Orders`) via AWS SAM, with two fully
isolated environments (dev/prod) — separate stacks, separate S3
artifact buckets, separate GitHub Actions pipelines — deployed through
OIDC-authenticated GitHub Actions. No application code: this lab is
purely infrastructure-as-code, verified through the AWS Console and the
AWS CLI.

## Table design

| | |
|---|---|
| Table name | `emmanuel-orders-<dev\|prod>` |
| Billing mode | `PAY_PER_REQUEST` (on-demand) |
| Table class | `STANDARD_INFREQUENT_ACCESS` (non-default, per rubric) |
| Primary key | `orderId` (partition) + `createdAt` (sort) |
| Non-key attributes | `totalAmount`, `region` |
| GSI1 — `CustomerOrdersIndex` | `customerId` (partition) + `createdAt` (sort) — a customer's order history, newest first |
| GSI2 — `StatusOrdersIndex` | `status` (partition) + `createdAt` (sort) — all orders in a given status, newest first |

`customerId` and `status` are themselves GSI partition keys, so they're
schema-significant rather than "plain" attributes — `totalAmount` and
`region` are the two attributes that exist purely as item data, never
part of any key.

## Architecture

See `infra/diagram/architecture.png` / `architecture.drawio` — two
parallel, independent pipelines (dev and prod), each with its own
GitHub Actions workflow, its own SAM artifact S3 bucket, and its own
CloudFormation stack, sharing one OIDC IAM role (both pipelines run
from the same branch, so one single-branch-scoped role covers both).

## Deployment

### One-time manual prerequisites

CloudShell (or any AWS CLI session with sufficient permissions) —
these can't be created by the pipelines themselves, since `sam deploy`
uploads *to* the artifact bucket, it doesn't create it:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

for ENV in dev prod; do
  BUCKET="emmanuel-orders-sam-artifacts-${ENV}-${ACCOUNT_ID}"
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
root) to create `github-actions-orders-dynamodb-push`, and add its ARN
as the `ORDERS_DYNAMODB_AWS_ROLE_ARN` GitHub secret (alongside the
already-shared `AWS_REGION` secret).

### Automated deploys

- **dev**: `.github/workflows/orders-dynamodb-deploy-dev.yml` — fires
  automatically on every push to `infra/**` on this branch.
- **prod**: `.github/workflows/orders-dynamodb-deploy-prod.yml` —
  fires only on a push that touches `infra/.promote-to-prod`. To
  promote, edit that file (bump its timestamp comment) and
  commit/push — routine infra changes never touch prod. (A
  `workflow_dispatch` gate was considered but doesn't work here: GitHub
  only exposes manual dispatch for a workflow that also exists on the
  repo's default branch, and this branch is intentionally never merged
  to `main` — so dispatch would be permanently unusable. The marker-file
  push trigger is the deliberate-but-actually-triggerable equivalent.)

### Manual local deploy (if needed)

```bash
cd infra
sam build
sam deploy --config-env dev   # or --config-env prod
```

## Verification

Console: DynamoDB → Tables → `emmanuel-orders-dev` (or `-prod`) →
confirm billing mode, table class, key schema, and both GSIs match the
table above.

CLI — seed sample data and query both indexes:

```bash
./scripts/seed-sample-orders.sh dev
```

See the script's own output for the exact `scan`/`query` commands it
suggests afterward.
