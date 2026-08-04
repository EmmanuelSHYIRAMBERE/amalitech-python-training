"""Admin-only endpoints for user management and usage statistics."""

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_admin
from app.auth.service import list_users
from app.dependencies import usage_tracker

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def get_users(admin: dict = Depends(require_admin)):  # noqa: B008
    """List all registered users (admin only)."""
    return {"users": list_users()}


@router.get("/usage")
def get_usage(admin: dict = Depends(require_admin)):  # noqa: B008
    """Return daily cost and total request counts (admin only)."""
    return {
        "daily_cost_usd": round(usage_tracker.get_daily_cost(), 6),
        "total_requests": usage_tracker.total_requests(),
    }
