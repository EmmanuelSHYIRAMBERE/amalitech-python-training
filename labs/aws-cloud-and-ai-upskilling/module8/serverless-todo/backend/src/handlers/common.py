"""Shared helpers for the serverless to-do app's Lambda handlers."""

import json
import os
from decimal import Decimal


def json_default(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError(f"Object of type {type(value)} is not JSON serializable")


def response(status_code, body=None):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body or {}, default=json_default),
    }


def get_user_id(event):
    """Extracts the Cognito sub (stable user ID) from the API Gateway
    Cognito authorizer's claims, injected into the request context.
    """
    return event["requestContext"]["authorizer"]["claims"]["sub"]


def tasks_table_name():
    return os.environ["TASKS_TABLE"]
