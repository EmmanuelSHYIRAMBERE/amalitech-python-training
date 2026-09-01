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
from diagrams.aws.devtools import Codepipeline, Codedeploy, Codebuild
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
        code = Java("Spring Boot App\n+ Dockerfile")
        repo = Github("Repository\n(feat/ecs-lab-ecs-cicd)")
        actions = GithubActions("GitHub Actions\n(ecs-lab.yml)")
        code >> Edge(label="git push app/**") >> repo
        repo >> Edge(label="triggers") >> actions

    with Cluster("Identity (OIDC — no stored keys)"):
        push_role = IAMRole("github-actions-ecs-lab-push")

    ecr = ECR("Amazon ECR\nemmanuel-ecs-lab-app\n(SHA tag + latest,\nlifecycle policy)")
    actions >> Edge(label="assumes role via OIDC") >> push_role
    push_role >> Edge(label="docker push\n(SHA + latest)") >> ecr

    with Cluster("CI/CD Pipeline"):
        eb = Eventbridge("EventBridge\nECR Push Rule")
        pipeline = Codepipeline("CodePipeline")
        build = Codebuild("CodeBuild\n(repackage\ndeploy spec)")
        deploy = Codedeploy("CodeDeploy\nBlue/Green")

        ecr >> Edge(label="PUSH event") >> eb
        eb >> Edge(label="starts") >> pipeline
        repo >> Edge(label="appspec/taskdef source", style="dashed", color="gray") >> pipeline
        pipeline >> build >> deploy

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
        cfn = Cloudformation("CloudFormation Git Sync\n(network.yaml +\napp-platform.yaml)")

    repo >> Edge(label="Git Sync watches infra/*.yaml", style="dashed", color="gray") >> cfn
    cfn >> Edge(label="provisions", style="dashed", color="gray") >> alb
