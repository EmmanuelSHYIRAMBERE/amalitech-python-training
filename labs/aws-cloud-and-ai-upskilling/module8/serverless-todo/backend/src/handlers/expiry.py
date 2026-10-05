"""Invoked once by EventBridge Scheduler, at a single task's Deadline.

Re-checks the task is still Pending before marking it Expired — this
guards against a race with the cancellation workflow (DynamoDB Streams
-> SQS FIFO -> Lambda), which may be deleting this same schedule at
roughly the same moment the schedule already fired. If the task is no
longer Pending (already Completed, already deleted, or already
Expired by a prior invocation), this is a no-op — idempotent by design.
"""

import os

import boto3
from botocore.exceptions import ClientError

from common import tasks_table_name

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")


def handler(event, context):
    user_id = event["UserId"]
    task_id = event["TaskId"]
    table = dynamodb.Table(tasks_table_name())

    try:
        result = table.update_item(
            Key={"UserId": user_id, "TaskId": task_id},
            UpdateExpression="SET #s = :expired",
            ConditionExpression="attribute_exists(TaskId) AND #s = :pending",
            ExpressionAttributeNames={"#s": "Status"},
            ExpressionAttributeValues={":expired": "Expired", ":pending": "Pending"},
            ReturnValues="ALL_NEW",
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            # Task already gone, or no longer Pending (Completed/already
            # Expired) — both are a legitimate no-op, not an error.
            return {"status": "skipped", "TaskId": task_id}
        raise

    task = result["Attributes"]
    sns.publish(
        TopicArn=os.environ["NOTIFICATIONS_TOPIC_ARN"],
        Subject="Task Expired",
        Message=(
            f"Your task has expired:\n\n"
            f"Description: {task.get('Description')}\n"
            f"Deadline: {task.get('Deadline')}\n"
        ),
    )

    return {"status": "expired", "TaskId": task_id}
