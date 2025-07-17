"""
Token Manager Service - Infrastructure Layer

This module provides JWT token creation, validation, and management functionality
for authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt, JWTError
from pydantic_settings import BaseSettings


class TokenSettings(BaseSettings):
    """JWT token configuration settings."""
    
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    reset_token_expire_minutes: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class TokenManager:
    """
    Service for JWT token management.
    
    Provides functionality for creating, validating, and decoding JWT tokens
    for authentication and password reset operations.
    """
    
    def __init__(self, settings: TokenSettings = None):
        """
        Initialize the token manager.
        
        Args:
            settings: Token configuration settings
        """
        self._settings = settings or TokenSettings()
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Dictionary containing token payload data
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self._settings.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(
            to_encode,
            self._settings.secret_key,
            algorithm=self._settings.algorithm
        )
    
    def create_reset_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT password reset token.
        
        Args:
            data: Dictionary containing token payload data
            
        Returns:
            JWT reset token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self._settings.reset_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "reset"})
        
        return jwt.encode(
            to_encode,
            self._settings.secret_key,
            algorithm=self._settings.algorithm
        )
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT access token.
        
        Args:
            token: JWT token string to decode
            
        Returns:
            Dictionary containing token payload
            
        Raises:
            TokenExpiredError: If token has expired
            TokenInvalidError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "access":
                raise TokenInvalidError("Invalid token type")
            
            return payload
            
        except JWTError:
            raise TokenInvalidError("Invalid token")
    
    def decode_reset_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT reset token.
        
        Args:
            token: JWT reset token string to decode
            
        Returns:
            Dictionary containing token payload
            
        Raises:
            TokenExpiredError: If token has expired
            TokenInvalidError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "reset":
                raise TokenInvalidError("Invalid token type")
            
            return payload
            
        except JWTError:
            raise TokenInvalidError("Invalid reset token")
    
    def get_token_expiry_seconds(self) -> int:
        """
        Get the access token expiry time in seconds.
        
        Returns:
            Token expiry time in seconds
        """
        return self._settings.access_token_expire_minutes * 60
    
    def get_reset_token_expiry_seconds(self) -> int:
        """
        Get the reset token expiry time in seconds.
        
        Returns:
            Reset token expiry time in seconds
        """
        return self._settings.reset_token_expire_minutes * 60
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired without raising an exception.
        
        Args:
            token: JWT token string to check
            
        Returns:
            True if token is expired, False otherwise
        """
        try:
            jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm]
            )
            return False
        except JWTError:
            return True
    
    def extract_user_id(self, token: str) -> Optional[str]:
        """
        Extract user ID from token without full validation.
        
        Args:
            token: JWT token string
            
        Returns:
            User ID if found, None otherwise
        """
        try:
            # Decode without verification for extraction only
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return payload.get("sub")
        except Exception:
            return None


class TokenError(Exception):
    """Base exception for token operations."""
    pass


class TokenExpiredError(TokenError):
    """Exception raised when a token has expired."""
    pass


class TokenInvalidError(TokenError):
    """Exception raised when a token is invalid."""
    pass
