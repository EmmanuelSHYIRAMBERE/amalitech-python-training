# Module 3 — Elastic Beanstalk Lab

Deploy a Node.js app to AWS Elastic Beanstalk with automated CI/CD via GitHub Actions and DynamoDB visit tracking.

---

## Architecture

```
GitHub Push
    │
    ▼
GitHub Actions
    ├── ZIP app → S3 (emmanuel-eb-lab-deployments)
    ├── Create EB application version
    └── Deploy to EB environment
                │
                ▼
    Elastic Beanstalk (Node.js 18, eu-north-1)
                │
                ▼
        DynamoDB (eb-lab-visits)
```

---

## One-Time Setup

### 1. Deploy infrastructure (DynamoDB + S3 + IAM)

```bash
aws cloudformation deploy \
  --template-file infrastructure.yaml \
  --stack-name emmanuel-eb-lab-infra \
  --capabilities CAPABILITY_NAMED_IAM \
  --region eu-north-1
```

### 2. Create Elastic Beanstalk application & environment

```bash
# Create application
aws elasticbeanstalk create-application \
  --application-name emmanuel-eb-lab \
  --region eu-north-1

# Create initial ZIP bundle
cd app && zip -r ../deploy-initial.zip . -x "*.git*" && cd ..

# Upload initial bundle to S3
aws s3 cp deploy-initial.zip s3://emmanuel-eb-lab-deployments/deploy-initial.zip

# Create initial application version
aws elasticbeanstalk create-application-version \
  --application-name emmanuel-eb-lab \
  --version-label v1-initial \
  --source-bundle S3Bucket=emmanuel-eb-lab-deployments,S3Key=deploy-initial.zip \
  --region eu-north-1

# Create environment (uses instance profile from CloudFormation)
aws elasticbeanstalk create-environment \
  --application-name emmanuel-eb-lab \
  --environment-name emmanuel-eb-lab-env \
  --solution-stack-name "64bit Amazon Linux 2023 v6.3.0 running Node.js 18" \
  --version-label v1-initial \
  --option-settings \
    Namespace=aws:autoscaling:launchconfiguration,OptionName=IamInstanceProfile,Value=emmanuel-eb-lab-instance-profile \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=DYNAMODB_TABLE,Value=eb-lab-visits \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=APP_VERSION,Value=1.0.0 \
  --region eu-north-1
```

### 3. Add GitHub Secrets

In your GitHub repo → Settings → Secrets → Actions:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | IAM user access key with EB + S3 permissions |
| `AWS_SECRET_ACCESS_KEY` | Corresponding secret key |

---

## CI/CD Flow

Every push to `feat/elastic-beanstalk-node-lab` that touches `app/**`:

1. ZIPs the `app/` directory
2. Uploads to `s3://emmanuel-eb-lab-deployments/`
3. Creates a new EB application version (labeled `v<run_number>-<sha>`)
4. Deploys to `emmanuel-eb-lab-env`
5. Waits for deployment to complete

---

## App Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | HTML page showing version + DynamoDB visit count |
| `GET /health` | JSON health check `{"status":"ok","version":"..."}` |

---

## Files

```
elastic-beanstalk-lab/
├── app/
│   ├── index.js          # Express app + DynamoDB integration
│   ├── package.json
│   ├── Procfile          # Tells EB how to start the app
│   └── .ebextensions/
│       └── env.config    # EB environment options
├── infrastructure.yaml   # CloudFormation: DynamoDB + S3 + IAM
└── README.md
```

---

## Deliverables

- [ ] Elastic Beanstalk URL responding in browser
- [ ] GitHub Actions workflow running on push
- [ ] New version visible in EB console after push
- [ ] DynamoDB visit count incrementing on each page load
