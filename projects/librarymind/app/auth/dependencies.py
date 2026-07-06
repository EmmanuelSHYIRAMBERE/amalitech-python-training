"""FastAPI dependencies for JWT authentication and role-based authorisation."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.auth.service import decode_access_token

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),  # noqa: B008
) -> dict:
    """Extract and validate the Bearer JWT. Returns {"username": ..., "role": ...}."""
    try:
        payload = decode_access_token(credentials.credentials)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if not username or not role:
            raise JWTError("Missing claims")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return {"username": username, "role": role}


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:  # noqa: B008
    """Extend get_current_user — raises 403 if the caller is not an admin."""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user
