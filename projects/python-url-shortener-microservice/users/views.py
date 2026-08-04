"""Auth views — Register, Login (JWT), Token Refresh."""

import logging

from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from shortener.throttles import LoginRateThrottle

from .models import User
from .serializers import RegisterSerializer, UserProfileSerializer

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """POST /api/v1/auth/register/ — create a new user account."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserProfileSerializer},
        summary="Register a new user",
    )
    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info("New user registered: username=%r", user.username)
        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/v1/auth/login/ — return JWT access + refresh tokens.

    Rate-limited to 5 attempts per minute per IP via LoginRateThrottle.
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                },
                "required": ["username", "password"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {"type": "object"},
                },
            }
        },
        summary="Login and obtain JWT tokens",
    )
    def post(self, request: Request) -> Response:
        username = request.data.get("username", "")
        password = request.data.get("password", "")

        abstract_user = authenticate(
            request=request, username=username, password=password
        )
        if abstract_user is None:
            logger.warning("Failed login attempt for username=%r", username)
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Re-fetch as concrete User so mypy and UserProfileSerializer are satisfied.
        try:
            user = User.objects.get(pk=abstract_user.pk)
        except User.DoesNotExist:  # pragma: no cover
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        logger.info("User logged in: username=%r", user.username)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserProfileSerializer(user).data,
            }
        )


class TokenRefreshView(BaseTokenRefreshView):
    """POST /api/v1/auth/refresh/ — exchange a refresh token for a new access token."""
