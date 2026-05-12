"""Custom DRF permission classes for the shortener project.

Hierarchy:
  IsOwnerOrReadOnly  — safe methods are open; writes require ownership.
  IsPremiumUser      — blocks non-premium users from premium-only actions.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from shortener.models import URL

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class IsOwnerOrReadOnly(BasePermission):
    """Allow any authenticated user to read; only the owner may write.

    Attach to detail views (URLDetailView).  The view must pass the URL
    instance as ``self.get_object()`` so ``has_object_permission`` is called.
    """

    message = "You do not have permission to modify another user's link."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request: Request, view: APIView, obj: URL) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsPremiumUser(BasePermission):
    """Allow access only to users with is_premium=True.

    Used to gate analytics detail and custom-alias creation.
    """

    message = "This feature is available to Premium users only."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user and request.user.is_authenticated and request.user.is_premium
        )
