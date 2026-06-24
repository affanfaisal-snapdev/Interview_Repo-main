"""
API routers for authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.base import get_db
from app.schemas.auth import (
    AuthenticatedUserResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth import AuthService

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Create a user account and return an access token.
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.register_user(request.email, request.password)
        access_token = auth_service.create_access_token(user)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=AuthenticatedUserResponse.model_validate(user),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and get an access token",
)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate a user and return an access token.
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(request.email, request.password)
        access_token = auth_service.create_access_token(user)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=AuthenticatedUserResponse.model_validate(user),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login user",
        )
