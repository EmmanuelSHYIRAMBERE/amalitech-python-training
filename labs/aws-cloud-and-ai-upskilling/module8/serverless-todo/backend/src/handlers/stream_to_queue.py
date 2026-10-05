"""DynamoDB Streams consumer — the first half of the cancellation
workflow. SAM's FilterCriteria on the event source already narrows
invocations to REMOVE events and MODIFY events where the new image's
Status is Completed, so every record this handler sees is one that
should cancel that task's scheduled expiry. This handler's only job is
to translate each stream record into a FIFO SQS message; the actual
cancellation (deleting the EventBridge schedule) happens in
cancellation.py, kept separate so the two concerns stay decoupled.
"""

import json
import os

import boto3

sqs = boto3.client("sqs")


def handler(event, context):
    queue_url = os.environ["CANCELLATION_QUEUE_URL"]

    for record in event["Records"]:
        # REMOVE records only have OldImage; MODIFY records (the
        # Completed-status transition) have both — NewImage is what we
        # filtered on, but either image carries the keys we need.
        image = record["dynamodb"].get("NewImage") or record["dynamodb"]["OldImage"]
        user_id = image["UserId"]["S"]
        task_id = image["TaskId"]["S"]

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({"UserId": user_id, "TaskId": task_id}),
            MessageGroupId=task_id,
        )

    return {"processed": len(event["Records"])}
