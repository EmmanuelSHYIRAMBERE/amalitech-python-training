"""Consumes the cancellation FIFO queue and deletes the matching
per-task EventBridge Scheduler schedule.

Idempotent by design: deleting an already-deleted schedule (or one
that already fired and self-deleted via ActionAfterCompletion=DELETE)
raises ResourceNotFoundException, which this handler treats as success
rather than an error — safe to process the same message more than
once, which SQS's at-least-once delivery can do even with FIFO queues.
"""

import json
import os

import boto3
from botocore.exceptions import ClientError

scheduler = boto3.client("scheduler")


def handler(event, context):
    group_name = os.environ["SCHEDULE_GROUP_NAME"]

    for record in event["Records"]:
        body = json.loads(record["body"])
        task_id = body["TaskId"]

        try:
            scheduler.delete_schedule(Name=task_id, GroupName=group_name)
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "ResourceNotFoundException":
                raise

    return {"processed": len(event["Records"])}
