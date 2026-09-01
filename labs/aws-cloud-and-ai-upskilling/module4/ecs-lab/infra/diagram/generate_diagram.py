"""Generates the ECS CI/CD Lab architecture diagram (network-architecture.png).

Requires: pip install diagrams, plus the Graphviz binary on PATH.
Run from anywhere: python generate_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import ECS, Fargate, ECR
from diagrams.aws.network import ELB, VPC, InternetGateway, PrivateSubnet, PublicSubnet, Endpoint
from diagrams.aws.security import IAMRole, IAM
from diagrams.aws.management import Cloudformation
from diagrams.aws.integration import Eventbridge
from diagrams.aws.devtools import Codepipeline, Codedeploy
from diagrams.aws.storage import S3
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import Users
from diagrams.programming.language import Java

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "nodesep": "0.6",
    "ranksep": "0.9",
}

with Diagram(
    "ECS CI/CD Lab — Network & Deployment Pipeline",
    filename="network-architecture",
    show=False,
    graph_attr=graph_attr,
    direction="LR",
):
    with Cluster("GitHub"):
        code = Java("Spring Boot App\n+ Dockerfile\n+ deploy-spec")
        repo = Github("Repository\n(feat/ecs-lab-ecs-cicd)")
        actions = GithubActions("GitHub Actions\n(ecs-lab.yml)")
        code >> Edge(label="git push app/**") >> repo
        repo >> Edge(label="triggers") >> actions

    with Cluster("Identity (OIDC — no stored keys)"):
        push_role = IAMRole("github-actions-ecs-lab-push")

    ecr = ECR("Amazon ECR\nemmanuel-ecs-lab-app\n(latest only,\nlifecycle policy)")
    actions >> Edge(label="assumes role via OIDC") >> push_role

    with Cluster("CI/CD Pipeline"):
        s3 = S3("Pipeline Artifact\nBucket (versioned)")
        eb = Eventbridge("EventBridge\nECR 'latest' Push Rule")
        pipeline = Codepipeline("CodePipeline")
        deploy = Codedeploy("CodeDeploy\nBlue/Green")

        push_role >> Edge(label="1. zip + upload\ndeploy-spec.zip") >> s3
        push_role >> Edge(label="2. docker push\n(latest)") >> ecr
        ecr >> Edge(label="PUSH event\n(tag=latest)") >> eb
        eb >> Edge(label="starts") >> pipeline
        s3 >> Edge(label="deploy-spec\nsource", style="dashed", color="gray") >> pipeline
        ecr >> Edge(label="image source", style="dashed", color="gray") >> pipeline
        pipeline >> deploy

    with Cluster("VPC 10.2.0.0/16 — eu-north-1 (2 AZs)"):
        user = Users("Internet\nVisitor")
        igw = InternetGateway("Internet\nGateway")

        with Cluster("Public Subnets"):
            alb = ELB("ALB\n(emmanuel-ecs-lab-alb)")

        with Cluster("Private Subnets (no NAT)"):
            with Cluster("ECS Fargate Service"):
                blue = Fargate("Blue Task Set")
                green = Fargate("Green Task Set")

            with Cluster("VPC Endpoints"):
                vpce = Endpoint("ecr.api / ecr.dkr\nlogs / s3 gateway")

        user >> Edge(label="HTTP :80") >> igw >> alb
        alb >> Edge(label="active", color="blue") >> blue
        alb >> Edge(label="idle", style="dashed", color="gray") >> green
        blue >> Edge(style="dashed", color="gray") >> vpce
        green >> Edge(style="dashed", color="gray") >> vpce

    deploy >> Edge(label="registers task def,\nshifts ALB traffic") >> alb

    with Cluster("Infrastructure as Code"):
        cfn = Cloudformation("CloudFormation Git Sync\n(network / ecr /\nalb-ecs / pipeline)")

    repo >> Edge(label="Git Sync watches infra/*.yaml", style="dashed", color="gray") >> cfn
    cfn >> Edge(label="provisions", style="dashed", color="gray") >> alb
