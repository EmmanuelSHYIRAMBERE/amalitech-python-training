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
    "nodesep": "0.6",
    "ranksep": "0.9",
    "pad": "0.5",
    "splines": "ortho",
}

with Diagram(
    "To-Do App Lab — Network & Deployment Pipeline",
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
        code = Java("Spring Boot App\n+ Dockerfile")
        repo = Github("Repository\n(feat/module6-todo-app)")
        actions = GithubActions("GitHub Actions\n(todo-app.yml)")
        push_role = IAMRole("OIDC role:\ngithub-actions-todo-app-push")
        ecr = ECR("Amazon ECR\n(emmanuel-todo-app,\nlatest only)")
        s3_artifacts = S3("Pipeline Artifact\nBucket (versioned)")
        eb = Eventbridge("EventBridge\n(ECR 'latest' push rule)")
        pipeline = Codepipeline("CodePipeline")
        deploy = Codedeploy("CodeDeploy\nBlue/Green")
        cfn = Cloudformation("CloudFormation Git Sync\n(network / database / cache /\necr / alb-ecs / pipeline)")

        code >> Edge(label="git push app/**") >> repo
        repo >> Edge(label="triggers") >> actions
        actions >> Edge(label="assumes via OIDC") >> push_role
        push_role >> Edge(label="docker push") >> ecr
        push_role >> Edge(label="upload deploy-spec.zip") >> s3_artifacts
        ecr >> Edge(label="PUSH event") >> eb
        eb >> Edge(label="starts") >> pipeline
        s3_artifacts >> Edge(label="deploy-spec source", style="dashed", color="gray") >> pipeline
        pipeline >> deploy
        repo >> Edge(label="Git Sync watches infra/*.yaml", style="dashed", color="gray") >> cfn

    user = Users("Internet\nVisitor")
    igw = InternetGateway("Internet\nGateway")

    with Cluster("Region — eu-north-1"):
        with Cluster("VPC — 10.4.0.0/16"):

            with Cluster("Availability Zone A"):
                with Cluster("Public subnet"):
                    with Cluster("Security group"):
                        alb_a = ELB("ALB\n(spans both AZs)")
                with Cluster("Private subnet — ECS"):
                    with Cluster("Security group"):
                        blue = Fargate("Blue Task Set\n(active)")
                with Cluster("Private subnet — DB + Proxy"):
                    with Cluster("SG: proxy"):
                        proxy = RDS("RDS Proxy")
                    with Cluster("SG: db"):
                        db = RDS("RDS PostgreSQL\n(db.t3.micro, Single-AZ)")
                with Cluster("Private subnet — Cache"):
                    with Cluster("Security group"):
                        cache = Elasticache("ElastiCache Redis\n(single node)")

                alb_a >> Edge(style="invis") >> blue >> Edge(style="invis") >> proxy >> Edge(style="invis") >> cache

            with Cluster("Availability Zone B"):
                with Cluster("Public subnet "):
                    with Cluster("Security group "):
                        alb_b = ELB("ALB\n(spans both AZs)")
                with Cluster("Private subnet — ECS "):
                    with Cluster("Security group  "):
                        green = Fargate("Green Task Set\n(idle)")
                with Cluster("Private subnet — DB + Proxy (standby) "):
                    with Cluster("SG: proxy "):
                        proxy_reserved = RDS("RDS Proxy ENI\n(standby AZ)")
                    with Cluster("SG: db "):
                        db_reserved = RDS(
                            "DB subnet group\n(reserved — no\nstandby today)"
                        )
                with Cluster("Private subnet — Cache "):
                    with Cluster("Security group   "):
                        cache_reserved = Elasticache(
                            "Cache subnet group\n(reserved — single\nnode today)"
                        )

                alb_b >> Edge(style="invis") >> green >> Edge(style="invis") >> proxy_reserved >> Edge(style="invis") >> cache_reserved

            # Invisible same-rank edge pins AZ A strictly left of AZ B.
            alb_a >> Edge(style="invis") >> alb_b

            vpce = Endpoint(
                "VPC Endpoints\necr.api / ecr.dkr / logs\nsecretsmanager"
            )
            s3_gw = S3("S3 Gateway\nEndpoint")

        user >> Edge(style="invis") >> igw
        igw >> alb_a
        igw >> alb_b
        alb_a >> Edge(label="active", color="blue") >> blue
        alb_b >> Edge(label="idle", style="dashed", color="gray") >> green
        blue >> Edge(label="writes (via proxy)") >> proxy
        proxy >> Edge(label="proxied conn") >> db
        green >> Edge(style="dashed", color="gray") >> proxy_reserved
        blue >> Edge(label="cached reads") >> cache
        green >> Edge(style="dashed", color="gray") >> cache_reserved
        blue >> Edge(style="dashed", color="gray") >> vpce
        green >> Edge(style="dashed", color="gray") >> vpce
        s3_gw >> Edge(style="dashed", color="gray") >> blue
        s3_gw >> Edge(style="dashed", color="gray") >> green

    # Pipeline → network references are drawn downward (pipeline was
    # defined first, so it already ranks above) — kept dashed/gray since
    # they're deploy-time actions, not steady-state traffic.
    deploy >> Edge(label="registers task def,\nshifts ALB traffic", style="dashed", color="gray") >> alb_a
    cfn >> Edge(label="provisions", style="dashed", color="gray") >> alb_a
