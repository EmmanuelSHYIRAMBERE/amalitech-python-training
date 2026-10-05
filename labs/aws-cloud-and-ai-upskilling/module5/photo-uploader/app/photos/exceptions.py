"""Custom DRF exception handler -- reshapes every error response into the
Node app's envelope: {success:false, statusCode, message}."""

from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    response = exception_handler(exc, context)
    if response is None:
        return None

    # Flatten DRF's default {"field": ["msg"]} / {"detail": "msg"} shapes
    # into a single message string, mirroring ErrorHandler's flat message.
    detail = response.data
    if isinstance(detail, dict):
        if "detail" in detail:
            message = str(detail["detail"])
        else:
            # first validation error message, any field
            first_key = next(iter(detail))
            first_val = detail[first_key]
            message = str(first_val[0] if isinstance(first_val, list) else first_val)
    elif isinstance(detail, list):
        message = str(detail[0])
    else:
        message = str(detail)

    response.data = {
        "success": False,
        "statusCode": response.status_code,
        "message": message,
    }
    return response
