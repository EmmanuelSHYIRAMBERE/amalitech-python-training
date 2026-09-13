"""Generates the To-Do App Lab architecture diagram (network-architecture.png).

Requires: pip install diagrams, plus the Graphviz binary on PATH.
Run from anywhere: python generate_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Fargate, ECR
from diagrams.aws.network import ELB, InternetGateway, Endpoint
from diagrams.aws.security import IAMRole
from diagrams.aws.management import Cloudformation
from diagrams.aws.integration import Eventbridge
from diagrams.aws.devtools import Codepipeline, Codedeploy
from diagrams.aws.storage import S3
from diagrams.aws.database import RDS, Elasticache
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import Users
from diagrams.programming.language import Java

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "nodesep": "0.8",
    "ranksep": "1.1",
    "pad": "0.5",
}

with Diagram(
    "To-Do App Lab — Network & Deployment Pipeline",
    filename="network-architecture",
    show=False,
    graph_attr=graph_attr,
    direction="LR",
):
    with Cluster("GitHub"):
        code = Java("Spring Boot App\n+ Dockerfile")
        repo = Github("Repository\n(feat/module6-todo-app)")
        actions = GithubActions("GitHub Actions\n(todo-app.yml)")
        code >> Edge(label="git push app/**") >> repo
        repo >> Edge(label="triggers") >> actions

    with Cluster("Identity (OIDC — no stored keys)"):
        push_role = IAMRole("github-actions-todo-app-push")

    ecr = ECR("Amazon ECR\nemmanuel-todo-app\n(latest only,\nlifecycle policy)")
    actions >> Edge(label="assumes role via OIDC") >> push_role

    with Cluster("CI/CD Pipeline"):
        s3_artifacts_icon = S3("Pipeline Artifact\nBucket (versioned)")
        eb = Eventbridge("EventBridge\nECR 'latest' Push Rule")
        pipeline = Codepipeline("CodePipeline")
        deploy = Codedeploy("CodeDeploy\nBlue/Green")

        push_role >> Edge(label="1. zip + upload\ndeploy-spec.zip") >> s3_artifacts_icon
        push_role >> Edge(label="2. docker push\n(latest)") >> ecr
        ecr >> Edge(label="PUSH event\n(tag=latest)") >> eb
        eb >> Edge(label="starts") >> pipeline
        s3_artifacts_icon >> Edge(label="deploy-spec\nsource", style="dashed", color="gray") >> pipeline
        ecr >> Edge(label="image source", style="dashed", color="gray") >> pipeline
        pipeline >> deploy

    with Cluster("VPC — eu-north-1 (2 AZs)"):
        user = Users("Internet\nVisitor")
        igw = InternetGateway("Internet\nGateway")

        with Cluster("Public Subnets"):
            alb = ELB("ALB\n(todo-app-alb)")

        with Cluster("Private Subnets (no NAT)"):
            with Cluster("ECS Subnets — Fargate Service"):
                blue = Fargate("Blue Task Set")
                green = Fargate("Green Task Set")

            with Cluster("VPC Endpoints (ECS subnets)"):
                vpce = Endpoint(
                    "ecr.api / ecr.dkr / logs\n"
                    "secretsmanager / s3 gateway\n"
                    "ssm / ssmmessages / ec2messages"
                )

            with Cluster("DB Subnets"):
                proxy = RDS("RDS Proxy\n(Secrets Manager auth)")
                db = RDS("RDS PostgreSQL\n(db.t3.micro)")
                proxy >> Edge(label="proxied connection") >> db

            with Cluster("Cache Subnets"):
                cache = Elasticache("ElastiCache Redis\n(cache.t3.micro,\nsingle node)")

        user >> Edge(label="HTTP :80") >> igw >> alb
        alb >> Edge(label="active", color="blue") >> blue
        alb >> Edge(label="idle", style="dashed", color="gray") >> green
        blue >> Edge(style="dashed", color="gray") >> vpce
        green >> Edge(style="dashed", color="gray") >> vpce
        blue >> Edge(label="writes (via proxy)") >> proxy
        green >> Edge(style="dashed", color="gray") >> proxy
        blue >> Edge(label="cached reads") >> cache
        green >> Edge(style="dashed", color="gray") >> cache

    deploy >> Edge(label="registers task def,\nshifts ALB traffic") >> alb

    with Cluster("Infrastructure as Code"):
        cfn = Cloudformation("CloudFormation Git Sync\n(network / database / cache /\necr / alb-ecs / pipeline)")

    repo >> Edge(label="Git Sync watches infra/*.yaml", style="dashed", color="gray") >> cfn
    cfn >> Edge(label="provisions", style="dashed", color="gray") >> alb
