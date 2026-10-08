"""Cognito PreSignUp trigger — auto-confirms every new user, per the lab
spec's "no manual verification" requirement.
"""


def handler(event, context):
    event["response"]["autoConfirmUser"] = True
    event["response"]["autoVerifyEmail"] = True
    return event
