"""Generates the Orders DynamoDB Lab architecture diagram (architecture.png).

Requires: pip install diagrams, plus the Graphviz binary on PATH.
Run from anywhere: python generate_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.database import Dynamodb
from diagrams.aws.management import Cloudformation
from diagrams.aws.security import IAMRole
from diagrams.aws.storage import S3
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "nodesep": "0.6",
    "ranksep": "0.9",
    "pad": "0.5",
    "splines": "ortho",
}

with Diagram(
    "Orders DynamoDB Lab — SAM Deployment Pipeline",
    filename="architecture",
    show=False,
    graph_attr=graph_attr,
    direction="TB",
):
    repo = Github("Repository\n(feat/module7-dynamodb-sam)")
    push_role = IAMRole("OIDC role:\ngithub-actions-orders-dynamodb-push")

    with Cluster("dev pipeline (auto, on push to infra/**)"):
        actions_dev = GithubActions("orders-dynamodb-\ndeploy-dev.yml")
        s3_dev = S3("SAM Artifact Bucket\n(dev)")
        cfn_dev = Cloudformation("emmanuel-orders-\ndynamodb-dev")
        table_dev = Dynamodb(
            "emmanuel-orders-dev\nPAY_PER_REQUEST,\nSTANDARD_INFREQUENT_ACCESS"
        )

        actions_dev >> Edge(label="sam build + deploy\n--config-env dev") >> s3_dev
        s3_dev >> Edge(label="template source") >> cfn_dev
        cfn_dev >> Edge(label="provisions") >> table_dev

    with Cluster("prod pipeline (manual workflow_dispatch only)"):
        actions_prod = GithubActions("orders-dynamodb-\ndeploy-prod.yml")
        s3_prod = S3("SAM Artifact Bucket\n(prod)")
        cfn_prod = Cloudformation("emmanuel-orders-\ndynamodb-prod")
        table_prod = Dynamodb(
            "emmanuel-orders-prod\nPAY_PER_REQUEST,\nSTANDARD_INFREQUENT_ACCESS"
        )

        actions_prod >> Edge(label="sam build + deploy\n--config-env prod") >> s3_prod
        s3_prod >> Edge(label="template source") >> cfn_prod
        cfn_prod >> Edge(label="provisions") >> table_prod

    repo >> Edge(label="push to infra/**") >> actions_dev
    repo >> Edge(label="workflow_dispatch\n(confirm='deploy')", style="dashed", color="gray") >> actions_prod
    actions_dev >> Edge(label="assumes via OIDC") >> push_role
    actions_prod >> Edge(label="assumes via OIDC") >> push_role
