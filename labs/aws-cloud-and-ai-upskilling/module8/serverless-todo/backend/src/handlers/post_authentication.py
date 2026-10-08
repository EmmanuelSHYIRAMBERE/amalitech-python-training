"""Cognito PostAuthentication trigger — subscribes the user's email to
the shared SNS notifications topic, per the lab spec. SNS itself
dedupes identical (protocol, endpoint) subscriptions, so a user
re-authenticating never creates duplicate subscriptions.
"""

import os

import boto3

sns = boto3.client("sns")


def handler(event, context):
    email = event["request"]["userAttributes"].get("email")
    if email:
        sns.subscribe(
            TopicArn=os.environ["NOTIFICATIONS_TOPIC_ARN"],
            Protocol="email",
            Endpoint=email,
        )
    return event
