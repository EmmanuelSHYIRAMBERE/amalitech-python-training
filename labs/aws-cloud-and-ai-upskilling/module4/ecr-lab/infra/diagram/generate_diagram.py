"""Generates the ECR Lab architecture diagram (network-architecture.png).

Requires: pip install diagrams, plus the Graphviz binary on PATH.
Run from anywhere: python generate_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import ECR
from diagrams.aws.security import IAMRole, IAM
from diagrams.aws.management import Cloudformation
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.programming.language import Typescript

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
}

with Diagram(
    "ECR Lab — Containerize & Push via OIDC",
    filename="network-architecture",
    show=False,
    graph_attr=graph_attr,
    direction="LR",
):
    with Cluster("Developer"):
        code = Typescript("Express/TS App\n+ Dockerfile")

    with Cluster("GitHub"):
        repo = Github("Repository\n(feat/ecr-lab-docker-push)")
        actions = GithubActions("GitHub Actions\nWorkflow (ecr-lab.yml)")
        code >> Edge(label="git push") >> repo
        repo >> Edge(label="triggers on\napp/** push") >> actions

    with Cluster("AWS (eu-north-1)"):
        with Cluster("Identity (OIDC — no stored keys)"):
            oidc_provider = IAM("OIDC Provider\ntoken.actions.githubusercontent.com")
            push_role = IAMRole("github-actions-ecr-push\n(least-privilege)")
            oidc_provider >> Edge(label="AssumeRoleWithWebIdentity\n(short-lived token)") >> push_role

        with Cluster("Infrastructure as Code"):
            cfn = Cloudformation("CloudFormation\nGit Sync")

        with Cluster("Container Registry"):
            ecr = ECR("Amazon ECR\nemmanuelshyirambere-nodeapp")

        actions >> Edge(label="assumes role via OIDC") >> push_role
        push_role >> Edge(label="docker push\n(image + scan)") >> ecr
        repo >> Edge(label="Git Sync watches\ninfra/ecr-repository.yaml", style="dashed", color="gray") >> cfn
        cfn >> Edge(label="provisions", style="dashed", color="gray") >> ecr
