"""Tasks CRUD Lambda, fronted by API Gateway's Cognito authorizer.

Routes (all under /tasks, scoped to the caller's own UserId):
  POST   /tasks            — create a task, schedule its expiry
  GET    /tasks             — list the caller's tasks
  PUT    /tasks/{taskId}    — update a task (e.g. mark Completed)
  DELETE /tasks/{taskId}    — delete a task

Creating a task also creates a one-time EventBridge Scheduler schedule
named after TaskId, firing at Deadline, invoking the expiry function —
the per-task "scheduled expiry event" the lab spec requires. That
schedule is left in place on update/delete; the separate DynamoDB
Streams -> SQS FIFO -> Lambda cancellation workflow is what actually
removes it when a task completes or is deleted, per the spec's
required architecture (this handler intentionally does NOT delete the
schedule itself, to keep the two workflows decoupled).
"""

import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import boto3
from boto3.dynamodb.conditions import Key

from common import get_user_id, response, tasks_table_name

dynamodb = boto3.resource("dynamodb")
scheduler = boto3.client("scheduler")

VALID_STATUSES = {"Pending", "Completed", "Expired"}


def _table():
    return dynamodb.Table(tasks_table_name())


def handler(event, context):
    method = event["httpMethod"]
    user_id = get_user_id(event)

    if method == "POST":
        return _create_task(event, user_id)
    if method == "GET":
        return _list_tasks(user_id)
    if method == "PUT":
        return _update_task(event, user_id)
    if method == "DELETE":
        return _delete_task(event, user_id)
    return response(405, {"message": "Method not allowed"})


def _create_task(event, user_id):
    body = json.loads(event.get("body") or "{}")
    description = body.get("Description")
    if not description:
        return response(400, {"message": "Description is required"})

    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    deadline_minutes = int(os.environ["TASK_DEADLINE_MINUTES"])
    deadline = now + timedelta(minutes=deadline_minutes)

    item = {
        "UserId": user_id,
        "TaskId": task_id,
        "Description": description,
        "Date": body.get("Date", now.date().isoformat()),
        "Status": "Pending",
        "Deadline": deadline.isoformat(),
        "CreatedAt": now.isoformat(),
    }
    _table().put_item(Item=item)
    _schedule_expiry(user_id, task_id, deadline)

    return response(201, item)


def _schedule_expiry(user_id, task_id, deadline):
    # EventBridge Scheduler one-time schedule, named by TaskId so the
    # cancellation workflow can delete it by that same name later.
    # UserId travels in the Input payload so the expiry function can
    # address the item by its full primary key (UserId + TaskId)
    # directly, instead of scanning the table to find it.
    scheduler.create_schedule(
        Name=task_id,
        GroupName=os.environ["SCHEDULE_GROUP_NAME"],
        ScheduleExpression=f"at({deadline.strftime('%Y-%m-%dT%H:%M:%S')})",
        FlexibleTimeWindow={"Mode": "OFF"},
        Target={
            "Arn": os.environ["EXPIRY_FUNCTION_ARN"],
            "RoleArn": os.environ["SCHEDULER_ROLE_ARN"],
            "Input": json.dumps({"UserId": user_id, "TaskId": task_id}),
        },
        ActionAfterCompletion="DELETE",
    )


def _list_tasks(user_id):
    result = _table().query(KeyConditionExpression=Key("UserId").eq(user_id))
    return response(200, {"tasks": result.get("Items", [])})


def _update_task(event, user_id):
    task_id = event["pathParameters"]["taskId"]
    body = json.loads(event.get("body") or "{}")

    update_fields = {}
    if "Description" in body:
        update_fields["Description"] = body["Description"]
    if "Date" in body:
        update_fields["Date"] = body["Date"]
    if "Status" in body:
        if body["Status"] not in VALID_STATUSES:
            return response(400, {"message": f"Status must be one of {sorted(VALID_STATUSES)}"})
        update_fields["Status"] = body["Status"]

    if not update_fields:
        return response(400, {"message": "No updatable fields provided"})

    expr_names = {f"#{k}": k for k in update_fields}
    expr_values = {f":{k}": v for k, v in update_fields.items()}
    update_expr = "SET " + ", ".join(f"#{k} = :{k}" for k in update_fields)

    try:
        result = _table().update_item(
            Key={"UserId": user_id, "TaskId": task_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ConditionExpression="attribute_exists(TaskId)",
            ReturnValues="ALL_NEW",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return response(404, {"message": "Task not found"})

    return response(200, result["Attributes"])


def _delete_task(event, user_id):
    task_id = event["pathParameters"]["taskId"]
    try:
        _table().delete_item(
            Key={"UserId": user_id, "TaskId": task_id},
            ConditionExpression="attribute_exists(TaskId)",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return response(404, {"message": "Task not found"})

    return response(204)
