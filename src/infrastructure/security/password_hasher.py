"""
Password Hasher Service - Infrastructure Layer

This module provides password hashing and verification functionality
using bcrypt for secure password storage.
"""

from passlib.context import CryptContext


class PasswordHasher:
    """
    Service for password hashing and verification.
    
    Uses bcrypt algorithm for secure password hashing with salt.
    This service is part of the infrastructure layer and provides
    concrete implementation for password security operations.
    """
    
    def __init__(self):
        """Initialize the password context with bcrypt."""
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
        """
        return self._pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        return self._pwd_context.verify(plain_password, hashed_password)
    
    def needs_update(self, hashed_password: str) -> bool:
        """
        Check if a hashed password needs to be updated.
        
        This is useful for migrating to newer hashing algorithms
        or updating hash parameters.
        
        Args:
            hashed_password: Hashed password to check
            
        Returns:
            True if hash needs update, False otherwise
        """
        return self._pwd_context.needs_update(hashed_password)
