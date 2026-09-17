"""Generates the Photo Uploader Lab architecture diagram (network-architecture.png).

Requires: pip install diagrams, plus the Graphviz binary on PATH.
Run from anywhere: python generate_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Fargate, ECR
from diagrams.aws.network import ELB, InternetGateway, Endpoint, CloudFront
from diagrams.aws.security import IAMRole
from diagrams.aws.management import Cloudformation
from diagrams.aws.integration import Eventbridge
from diagrams.aws.devtools import Codepipeline, Codedeploy
from diagrams.aws.storage import S3
from diagrams.aws.database import RDS
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import Users
from diagrams.programming.language import Python

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "nodesep": "0.6",
    "ranksep": "0.9",
    "pad": "0.5",
    "splines": "ortho",
}

with Diagram(
    "Photo Uploader Lab — Network & Deployment Pipeline",
    filename="network-architecture",
    show=False,
    graph_attr=graph_attr,
    direction="TB",
):
    with Cluster("GitHub"):
        code = Python("Django/DRF App\n+ Dockerfile")
        repo = Github("Repository\n(feat/module5-photo-uploader)")
        actions = GithubActions("GitHub Actions\n(photo-uploader.yml)")
        code >> Edge(label="git push app/**") >> repo
        repo >> Edge(label="triggers") >> actions

    with Cluster("Identity (OIDC — no stored keys)"):
        push_role = IAMRole("github-actions-photo-uploader-push")

    ecr = ECR("Amazon ECR\nemmanuel-photo-uploader-app\n(latest only,\nlifecycle policy)")
    actions >> Edge(label="assumes role via OIDC") >> push_role

    with Cluster("CI/CD Pipeline"):
        s3_artifacts = S3("Pipeline Artifact\nBucket (versioned)")
        eb = Eventbridge("EventBridge\nECR 'latest' Push Rule")
        pipeline = Codepipeline("CodePipeline")
        deploy = Codedeploy("CodeDeploy\nBlue/Green")

        push_role >> Edge(label="1. zip + upload\ndeploy-spec.zip") >> s3_artifacts
        push_role >> Edge(label="2. docker push\n(latest)") >> ecr
        ecr >> Edge(label="PUSH event\n(tag=latest)") >> eb
        eb >> Edge(label="starts") >> pipeline
        s3_artifacts >> Edge(label="deploy-spec\nsource", style="dashed", color="gray") >> pipeline
        ecr >> Edge(label="image source", style="dashed", color="gray") >> pipeline
        pipeline >> deploy

    user = Users("Internet\nVisitor")
    igw = InternetGateway("Internet\nGateway")

    with Cluster("Region — eu-north-1"):
        with Cluster("VPC — 10.3.0.0/16"):

            with Cluster("Availability Zone A"):
                with Cluster("Public subnet — ALB"):
                    alb_a = ELB("ALB\n(spans both AZs)")
                with Cluster("Private subnet — ECS"):
                    blue = Fargate("Blue Task Set")
                with Cluster("Private subnet — Database"):
                    db = RDS("RDS PostgreSQL\n(db.t3.micro, Single-AZ)\ncredentials via\nSecrets Manager")

                alb_a >> Edge(style="invis") >> blue >> Edge(style="invis") >> db

            with Cluster("Availability Zone B"):
                with Cluster("Public subnet — ALB "):
                    alb_b = ELB("ALB\n(spans both AZs)")
                with Cluster("Private subnet — ECS "):
                    green = Fargate("Green Task Set")
                with Cluster("Private subnet — Database "):
                    db_reserved = RDS("(DB subnet group\nreserved capacity —\nno standby today)")

                alb_b >> Edge(style="invis") >> green >> Edge(style="invis") >> db_reserved

            with Cluster("VPC Endpoints (ECS subnets only)"):
                vpce = Endpoint(
                    "ecr.api / ecr.dkr / logs\n"
                    "secretsmanager\n"
                    "ssm / ssmmessages / ec2messages"
                )
                s3_gw = S3("S3 Gateway\nEndpoint")

        user >> Edge(label="HTTP :80") >> igw
        igw >> alb_a
        igw >> alb_b
        alb_a >> Edge(label="active", color="blue") >> blue
        alb_b >> Edge(label="idle", style="dashed", color="gray") >> green
        blue >> Edge(style="dashed", color="gray") >> vpce
        green >> Edge(style="dashed", color="gray") >> vpce
        blue >> Edge(label="photo metadata") >> db
        green >> Edge(style="dashed", color="gray") >> db
        s3_gw >> Edge(style="dashed", color="gray") >> blue
        s3_gw >> Edge(style="dashed", color="gray") >> green

    deploy >> Edge(label="registers task def,\nshifts ALB traffic") >> alb_a

    with Cluster("Image Delivery"):
        photos_bucket = S3("Photos Bucket\n(private, no public access)")
        cdn = CloudFront("CloudFront Distribution\n(Price Class 200)")

        cdn >> Edge(label="Origin Access Control\n(OAC)", color="darkgreen") >> photos_bucket
        blue >> Edge(label="upload photo") >> photos_bucket
        user >> Edge(label="view images", color="darkgreen") >> cdn

    with Cluster("Infrastructure as Code"):
        cfn = Cloudformation("CloudFormation Git Sync\n(network / storage / database /\necr / alb-ecs / pipeline)")

    repo >> Edge(label="Git Sync watches infra/*.yaml", style="dashed", color="gray") >> cfn
    cfn >> Edge(label="provisions", style="dashed", color="gray") >> alb_a
