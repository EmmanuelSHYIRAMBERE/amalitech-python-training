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
    # ── Deployment pipeline (drawn first so it ranks ABOVE the network
    # section — every edge below points downward into the network, never
    # back up, so Graphviz's TB layout can't drag this section out of
    # order the way an upward edge would). ──
    with Cluster("Deployment Pipeline (GitHub → OIDC → ECR → CodePipeline → CodeDeploy)"):
        code = Python("Django/DRF App\n+ Dockerfile")
        repo = Github("Repository\n(feat/module5-photo-uploader)")
        actions = GithubActions("GitHub Actions\n(photo-uploader.yml)")
        push_role = IAMRole("OIDC role:\ngithub-actions-photo-uploader-push")
        ecr = ECR("Amazon ECR\n(emmanuel-photo-uploader-app,\nlatest only)")
        s3_artifacts = S3("Pipeline Artifact\nBucket (versioned)")
        eb = Eventbridge("EventBridge\n(ECR 'latest' push rule)")
        pipeline = Codepipeline("CodePipeline")
        deploy = Codedeploy("CodeDeploy\nBlue/Green")
        cfn = Cloudformation("CloudFormation nested stacks\n(root.yaml via GitHub Actions)")

        code >> Edge(label="git push app/**") >> repo
        repo >> Edge(label="triggers") >> actions
        actions >> Edge(label="assumes via OIDC") >> push_role
        push_role >> Edge(label="docker push") >> ecr
        push_role >> Edge(label="upload deploy-spec.zip") >> s3_artifacts
        ecr >> Edge(label="PUSH event") >> eb
        eb >> Edge(label="starts") >> pipeline
        s3_artifacts >> Edge(label="deploy-spec source", style="dashed", color="gray") >> pipeline
        pipeline >> deploy
        repo >> Edge(label="push to infra/**", style="dashed", color="gray") >> cfn

    user = Users("Internet\nVisitor")
    igw = InternetGateway("Internet\nGateway")

    with Cluster("Region — eu-north-1"):
        with Cluster("VPC — 10.3.0.0/16"):

            with Cluster("Availability Zone A"):
                with Cluster("Public subnet"):
                    with Cluster("Security group"):
                        alb_a = ELB("ALB\n(spans both AZs)")
                with Cluster("Private subnet — ECS"):
                    with Cluster("Security group"):
                        blue = Fargate("Blue Task Set\n(active)")
                with Cluster("Private subnet — Database"):
                    with Cluster("Security group"):
                        db = RDS("RDS PostgreSQL\n(db.t3.micro, Single-AZ)")

                alb_a >> Edge(style="invis") >> blue >> Edge(style="invis") >> db

            with Cluster("Availability Zone B"):
                with Cluster("Public subnet "):
                    with Cluster("Security group "):
                        alb_b = ELB("ALB\n(spans both AZs)")
                with Cluster("Private subnet — ECS "):
                    with Cluster("Security group  "):
                        green = Fargate("Green Task Set\n(idle)")
                with Cluster("Private subnet — Database "):
                    with Cluster("Security group   "):
                        db_reserved = RDS(
                            "DB subnet group\n(reserved — no\nstandby today)"
                        )

                alb_b >> Edge(style="invis") >> green >> Edge(style="invis") >> db_reserved

            # Invisible same-rank edge pins AZ A strictly left of AZ B —
            # without it, Graphviz's default ordering heuristic is free
            # to place them in either left-right order.
            alb_a >> Edge(style="invis") >> alb_b

            vpce = Endpoint("VPC Endpoints\necr.api / ecr.dkr / logs\nsecretsmanager")
            s3_gw = S3("S3 Gateway\nEndpoint")

        user >> Edge(style="invis") >> igw
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

    with Cluster("Image Delivery"):
        photos_bucket = S3("Photos Bucket\n(private, OAC only)")
        cdn = CloudFront("CloudFront\n(Price Class 200)")

        cdn >> Edge(label="OAC", color="darkgreen") >> photos_bucket
        blue >> Edge(label="upload photo") >> photos_bucket
        user >> Edge(label="view images", color="darkgreen") >> cdn

    # Pipeline → network references are drawn downward (pipeline was
    # defined first, so it already ranks above) — kept dashed/gray since
    # they're deploy-time actions, not steady-state traffic.
    deploy >> Edge(label="registers task def,\nshifts ALB traffic", style="dashed", color="gray") >> alb_a
    cfn >> Edge(label="provisions", style="dashed", color="gray") >> alb_a
