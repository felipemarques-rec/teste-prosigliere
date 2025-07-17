"""
Authentication Use Cases - Domain Layer

This module contains the application business rules for authentication operations.
Following Clean Architecture principles, these use cases:
- Orchestrate the flow of data to and from entities
- Implement authentication-specific business rules
- Are independent of frameworks and external concerns
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..entities.user import User
from ..repositories.user_repository import (
    UserRepository,
    UserNotFoundError,
    DuplicateUserError
)


class AuthUseCases:
    """
    Use cases for authentication operations.
    
    This class implements the application business rules for user authentication,
    registration, and session management while maintaining business logic integrity.
    
    Following the Single Responsibility Principle, this class focuses solely
    on authentication-related business operations.
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: 'PasswordHasher',
        token_manager: 'TokenManager'
    ):
        """
        Initialize the authentication use cases.
        
        Args:
            user_repository: Repository for user persistence
            password_hasher: Service for password hashing and verification
            token_manager: Service for JWT token management
        """
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_manager = token_manager
    
    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        Register a new user.
        
        Business Rules:
        - Username must be unique
        - Email must be unique
        - Password must meet security requirements
        - User is active by default
        
        Args:
            username: Desired username
            email: Email address
            password: Plain text password
            full_name: Full name (optional)
            
        Returns:
            The created User entity
            
        Raises:
            ValueError: If input validation fails
            DuplicateUserError: If username or email already exists
        """
        # Validate password strength
        self._validate_password_strength(password)
        
        # Check if username already exists
        if await self._user_repository.exists_by_username(username):
            raise DuplicateUserError(username, "username")
        
        # Check if email already exists
        if await self._user_repository.exists_by_email(email):
            raise DuplicateUserError(email, "email")
        
        # Hash the password
        password_hash = self._password_hasher.hash_password(password)
        
        # Create user entity
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name
        )
        
        # Persist the user
        return await self._user_repository.create(user)
    
    async def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username/email and password.
        
        Business Rules:
        - User can login with either username or email
        - User must be active to authenticate
        - Password must match the stored hash
        
        Args:
            username_or_email: Username or email address
            password: Plain text password
            
        Returns:
            User entity if authentication successful, None otherwise
        """
        # Try to find user by username first, then by email
        user = await self._user_repository.get_by_username(username_or_email)
        if not user:
            user = await self._user_repository.get_by_email(username_or_email)
        
        # If user not found or inactive, authentication fails
        if not user or not user.is_active:
            return None
        
        # Verify password
        if not self._password_hasher.verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def create_access_token(self, user: User) -> dict:
        """
        Create an access token for the authenticated user.
        
        Args:
            user: Authenticated user entity
            
        Returns:
            Dictionary containing token information
        """
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser
        }
        
        access_token = self._token_manager.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self._token_manager.get_token_expiry_seconds(),
            "user": user.to_dict()
        }
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get the current user from a JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            User entity if token is valid, None otherwise
        """
        try:
            # Decode and validate token
            payload = self._token_manager.decode_token(token)
            user_id = UUID(payload.get("sub"))
            
            # Get user from repository
            user = await self._user_repository.get_by_id(user_id)
            
            # Check if user is still active
            if user and user.is_active:
                return user
            
            return None
            
        except Exception:
            return None
    
    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Business Rules:
        - Current password must be correct
        - New password must meet security requirements
        - New password must be different from current password
        
        Args:
            user_id: ID of the user
            current_password: Current plain text password
            new_password: New plain text password
            
        Returns:
            True if password changed successfully
            
        Raises:
            UserNotFoundError: If user doesn't exist
            ValueError: If validation fails
        """
        # Get user
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        
        # Verify current password
        if not self._password_hasher.verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Validate new password strength
        self._validate_password_strength(new_password)
        
        # Check if new password is different
        if self._password_hasher.verify_password(new_password, user.password_hash):
            raise ValueError("New password must be different from current password")
        
        # Hash new password and update user
        new_password_hash = self._password_hasher.hash_password(new_password)
        user.update_password_hash(new_password_hash)
        
        # Save updated user
        await self._user_repository.update(user)
        
        return True
    
    async def reset_password(self, email: str) -> bool:
        """
        Initiate password reset process.
        
        Business Rule: Only active users can reset passwords.
        
        Args:
            email: Email address of the user
            
        Returns:
            True if reset initiated (always returns True for security)
        """
        # Find user by email
        user = await self._user_repository.get_by_email(email)
        
        # For security reasons, always return True even if user doesn't exist
        if not user or not user.is_active:
            return True
        
        # Generate reset token (implementation would send email)
        reset_token = self._token_manager.create_reset_token({"user_id": str(user.id)})
        
        # In a real implementation, you would send an email with the reset token
        # For now, we just log it (in production, use proper logging)
        print(f"Password reset token for {email}: {reset_token}")
        
        return True
    
    async def confirm_password_reset(
        self,
        reset_token: str,
        new_password: str
    ) -> bool:
        """
        Confirm password reset with token.
        
        Args:
            reset_token: Password reset token
            new_password: New plain text password
            
        Returns:
            True if password reset successfully
            
        Raises:
            ValueError: If token is invalid or password validation fails
        """
        try:
            # Decode reset token
            payload = self._token_manager.decode_reset_token(reset_token)
            user_id = UUID(payload.get("user_id"))
            
            # Get user
            user = await self._user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                raise ValueError("Invalid reset token")
            
            # Validate new password
            self._validate_password_strength(new_password)
            
            # Hash new password and update user
            new_password_hash = self._password_hasher.hash_password(new_password)
            user.update_password_hash(new_password_hash)
            
            # Save updated user
            await self._user_repository.update(user)
            
            return True
            
        except Exception:
            raise ValueError("Invalid or expired reset token")
    
    def _validate_password_strength(self, password: str) -> None:
        """
        Validate password strength.
        
        Business Rules:
        - Password must be at least 8 characters long
        - Password must contain at least one uppercase letter
        - Password must contain at least one lowercase letter
        - Password must contain at least one digit
        - Password must contain at least one special character
        
        Args:
            password: Plain text password to validate
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            raise ValueError("Password must contain at least one special character")


class AuthUseCaseError(Exception):
    """Base exception for authentication use case operations."""
    pass


class InvalidCredentialsError(AuthUseCaseError):
    """Exception raised when authentication credentials are invalid."""
    pass


class TokenExpiredError(AuthUseCaseError):
    """Exception raised when a token has expired."""
    pass


class InactiveUserError(AuthUseCaseError):
    """Exception raised when trying to authenticate an inactive user."""
    pass
