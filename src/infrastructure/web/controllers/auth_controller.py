"""
Authentication Controller - Infrastructure Layer

This module contains the FastAPI route handlers for authentication operations.
Following Clean Architecture principles, this controller:
- Handles HTTP requests and responses
- Delegates business logic to use cases
- Manages authentication and authorization
- Provides proper error handling and status codes
"""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities.user import User
from ....domain.use_cases.auth_use_cases import AuthUseCases
from ....domain.repositories.user_repository import (
    DuplicateUserError,
    UserNotFoundError
)
from ....infrastructure.database.database import get_database_session
from ....infrastructure.database.repositories.user_repository import UserRepositoryImpl
from ....infrastructure.security.password_hasher import PasswordHasher
from ....infrastructure.security.token_manager import TokenManager, TokenExpiredError, TokenInvalidError
from ..schemas.auth_schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    UserResponse,
    TokenResponse,
    MessageResponse,
    ErrorResponse
)


logger = logging.getLogger(__name__)

# Create router with authentication prefix
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for JWT tokens
security = HTTPBearer()


async def get_auth_use_cases(
    session: Annotated[AsyncSession, Depends(get_database_session)]
) -> AuthUseCases:
    """
    Dependency to create AuthUseCases with required dependencies.
    
    Args:
        session: Database session
        
    Returns:
        Configured AuthUseCases instance
    """
    user_repository = UserRepositoryImpl(session)
    password_hasher = PasswordHasher()
    token_manager = TokenManager()
    
    return AuthUseCases(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_manager=token_manager
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)]
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        auth_use_cases: Authentication use cases
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        user = await auth_use_cases.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user
    except (TokenExpiredError, TokenInvalidError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username, email, and password"
)
async def register_user(
    user_data: UserRegistrationRequest,
    auth_use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)]
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        auth_use_cases: Authentication use cases
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        user = await auth_use_cases.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        logger.info(f"User registered successfully: {user.username}")
        return UserResponse.from_orm(user)
        
    except DuplicateUserError as e:
        logger.warning(f"Registration failed - duplicate user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        logger.warning(f"Registration failed - validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed - unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return access token"
)
async def login_user(
    login_data: UserLoginRequest,
    auth_use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)]
):
    """
    Authenticate user and return access token.
    
    Args:
        login_data: User login credentials
        auth_use_cases: Authentication use cases
        
    Returns:
        Access token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        user = await auth_use_cases.authenticate_user(
            username_or_email=login_data.username_or_email,
            password=login_data.password
        )
        
        if not user:
            logger.warning(f"Login failed for: {login_data.username_or_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password"
            )
        
        token_data = await auth_use_cases.create_access_token(user)
        logger.info(f"User logged in successfully: {user.username}")
        
        return TokenResponse(**token_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed - unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user"
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return UserResponse.from_orm(current_user)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change the password for the currently authenticated user"
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)]
):
    """
    Change user password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_use_cases: Authentication use cases
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If password change fails
    """
    try:
        await auth_use_cases.change_password(
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        logger.info(f"Password changed successfully for user: {current_user.username}")
        return MessageResponse(message="Password changed successfully")
        
    except ValueError as e:
        logger.warning(f"Password change failed for {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password change failed - unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Request a password reset token to be sent to the user's email"
)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    auth_use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)]
):
    """
    Request password reset.
    
    Args:
        reset_data: Password reset request data
        auth_use_cases: Authentication use cases
        
    Returns:
        Success message
    """
    try:
        await auth_use_cases.reset_password(reset_data.email)
        logger.info(f"Password reset requested for email: {reset_data.email}")
        
        # Always return success for security reasons
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )
        
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        # Still return success for security reasons
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )


@router.post(
    "/reset-password/confirm",
    response_model=MessageResponse,
    summary="Confirm password reset",
    description="Confirm password reset using the reset token"
)
async def confirm_password_reset(
    reset_data: PasswordResetConfirmRequest,
    auth_use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)]
):
    """
    Confirm password reset.
    
    Args:
        reset_data: Password reset confirmation data
        auth_use_cases: Authentication use cases
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If reset confirmation fails
    """
    try:
        await auth_use_cases.confirm_password_reset(
            reset_token=reset_data.reset_token,
            new_password=reset_data.new_password
        )
        
        logger.info("Password reset confirmed successfully")
        return MessageResponse(message="Password reset successfully")
        
    except ValueError as e:
        logger.warning(f"Password reset confirmation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password reset confirmation failed - unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
