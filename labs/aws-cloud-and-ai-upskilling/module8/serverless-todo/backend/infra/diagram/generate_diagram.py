"""Generates the Serverless To-Do Lab architecture diagram (architecture.png).

Requires: pip install diagrams, plus the Graphviz binary on PATH.
Run from anywhere: python generate_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge, SimpleNotificationServiceSns, SimpleQueueServiceSqs
from diagrams.aws.management import Cloudwatch
from diagrams.aws.mobile import Amplify
from diagrams.aws.network import APIGateway
from diagrams.aws.security import Cognito
from diagrams.onprem.client import Users

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "nodesep": "0.6",
    "ranksep": "0.9",
    "pad": "0.5",
    "splines": "ortho",
}

with Diagram(
    "Serverless To-Do Lab — Architecture",
    filename="architecture",
    show=False,
    graph_attr=graph_attr,
    direction="TB",
):
    user = Users("End User")

    with Cluster("Frontend (AWS Amplify Hosting)"):
        frontend = Amplify("Static site\n(HTML/CSS/JS)")

    with Cluster("Auth"):
        user_pool = Cognito("Cognito User Pool")
        presignup = Lambda("PreSignUp\n(auto-confirm)")
        postauth = Lambda("PostAuthentication\n(subscribe to SNS)")
        user_pool >> Edge(label="triggers", style="dashed", color="gray") >> presignup
        user_pool >> Edge(label="triggers", style="dashed", color="gray") >> postauth

    with Cluster("API"):
        api = APIGateway("Tasks REST API\n(Cognito authorizer)")
        tasks_fn = Lambda("Tasks CRUD\nLambda")
        api >> tasks_fn

    table = Dynamodb("Tasks Table\n(PK: UserId, SK: TaskId)\nStreams enabled")

    with Cluster("Expiry workflow"):
        scheduler = Eventbridge("EventBridge Scheduler\n(one-time, per TaskId)")
        expiry_fn = Lambda("Expiry Lambda")
        scheduler >> expiry_fn

    with Cluster("Cancellation workflow (decoupled, idempotent)"):
        stream_fn = Lambda("Stream-to-Queue\nLambda")
        queue = SimpleQueueServiceSqs("Cancellation\nSQS FIFO")
        cancel_fn = Lambda("Cancellation\nLambda")
        stream_fn >> Edge(label="enqueue") >> queue >> Edge(label="consume") >> cancel_fn

    sns = SimpleNotificationServiceSns("Notifications Topic\n(email)")
    cloudwatch = Cloudwatch("CloudWatch\nLogs & Metrics")

    user >> Edge(label="sign up / sign in") >> user_pool
    user >> Edge(label="HTTPS") >> frontend
    frontend >> Edge(label="Bearer: ID token") >> api

    postauth >> Edge(label="sns:Subscribe") >> sns

    tasks_fn >> Edge(label="CRUD") >> table
    tasks_fn >> Edge(label="create one-time\nschedule per task") >> scheduler

    table >> Edge(label="DynamoDB Streams\n(REMOVE / Status=Completed)") >> stream_fn

    expiry_fn >> Edge(label="update Status=Expired\n(if still Pending)") >> table
    expiry_fn >> Edge(label="sns:Publish") >> sns

    cancel_fn >> Edge(label="scheduler:DeleteSchedule") >> scheduler

    for fn in [presignup, postauth, tasks_fn, expiry_fn, stream_fn, cancel_fn]:
        fn >> Edge(style="dashed", color="gray") >> cloudwatch
