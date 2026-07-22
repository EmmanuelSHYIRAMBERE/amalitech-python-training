"""Authentication service: user store, password hashing, JWT creation/verification."""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# username → {"password_hash": str, "role": str}
_users: dict[str, dict] = {}


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def register_user(username: str, password: str, role: str = "user") -> dict:
    """Register a new user. Raises ValueError if username already taken."""
    if username in _users:
        raise ValueError(f"Username '{username}' is already taken.")
    _users[username] = {"password_hash": hash_password(password), "role": role}
    return {"username": username, "role": role}


def authenticate_user(username: str, password: str) -> dict | None:
    """Return user dict if credentials are valid, else None."""
    user = _users.get(username)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return {"username": username, "role": user["role"]}


def create_access_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT. Raises JWTError on failure."""
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


def list_users() -> list[dict]:
    return [{"username": u, "role": d["role"]} for u, d in _users.items()]
