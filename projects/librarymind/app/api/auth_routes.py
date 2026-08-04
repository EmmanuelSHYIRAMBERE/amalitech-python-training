"""Authentication endpoints: register and login."""

from fastapi import APIRouter, HTTPException, status

from app.auth.models import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.auth.service import authenticate_user, create_access_token, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(req: RegisterRequest):
    """Register a new user account (role defaults to 'user')."""
    try:
        user = register_user(req.username, req.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return user


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    """Exchange credentials for a JWT Bearer token."""
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user["username"], user["role"])
    return TokenResponse(access_token=token)
