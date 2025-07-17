"""
User Entity - Domain Layer

This module contains the User entity which represents the core business logic
for users without any framework dependencies.

Following Clean Architecture principles, this entity contains:
- Business rules and validation logic
- Domain-specific behavior
- No dependencies on external frameworks or infrastructure
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import re


@dataclass
class User:
    """
    User entity representing a user in the domain.
    
    This entity encapsulates the business rules for users:
    - Email must be valid and unique
    - Username must be between 3 and 50 characters
    - Password must meet security requirements
    - Created and updated timestamps are managed automatically
    - Each user has a unique identifier
    
    Attributes:
        id: Unique identifier for the user
        username: Username (3-50 characters, alphanumeric + underscore)
        email: Email address (must be valid format)
        password_hash: Hashed password (stored securely)
        full_name: Full name of the user (optional)
        is_active: Whether the user account is active
        is_superuser: Whether the user has admin privileges
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
    """
    
    username: str
    email: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)
    full_name: Optional[str] = field(default=None)
    is_active: bool = field(default=True)
    is_superuser: bool = field(default=False)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate the user data after initialization."""
        self._validate_username()
        self._validate_email()
        self._validate_password_hash()
        if self.full_name:
            self._validate_full_name()
    
    def _validate_username(self) -> None:
        """
        Validate the username.
        
        Business Rules:
        - Username must be a string
        - Username must be between 3 and 50 characters
        - Username can only contain alphanumeric characters and underscores
        - Username cannot start or end with underscore
        
        Raises:
            ValueError: If username validation fails
        """
        if not isinstance(self.username, str):
            raise ValueError("Username must be a string")
        
        if not self.username.strip():
            raise ValueError("Username cannot be empty")
        
        username = self.username.strip()
        
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if len(username) > 50:
            raise ValueError("Username cannot exceed 50 characters")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        if username.startswith('_') or username.endswith('_'):
            raise ValueError("Username cannot start or end with underscore")
        
        self.username = username
    
    def _validate_email(self) -> None:
        """
        Validate the email address.
        
        Business Rules:
        - Email must be a string
        - Email must have valid format
        - Email cannot exceed 255 characters
        
        Raises:
            ValueError: If email validation fails
        """
        if not isinstance(self.email, str):
            raise ValueError("Email must be a string")
        
        if not self.email.strip():
            raise ValueError("Email cannot be empty")
        
        email = self.email.strip().lower()
        
        if len(email) > 255:
            raise ValueError("Email cannot exceed 255 characters")
        
        # Basic email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Email must have a valid format")
        
        self.email = email
    
    def _validate_password_hash(self) -> None:
        """
        Validate the password hash.
        
        Business Rules:
        - Password hash must be a string
        - Password hash cannot be empty
        
        Raises:
            ValueError: If password hash validation fails
        """
        if not isinstance(self.password_hash, str):
            raise ValueError("Password hash must be a string")
        
        if not self.password_hash.strip():
            raise ValueError("Password hash cannot be empty")
    
    def _validate_full_name(self) -> None:
        """
        Validate the full name.
        
        Business Rules:
        - Full name must be a string if provided
        - Full name cannot exceed 100 characters
        
        Raises:
            ValueError: If full name validation fails
        """
        if self.full_name is not None:
            if not isinstance(self.full_name, str):
                raise ValueError("Full name must be a string")
            
            if len(self.full_name.strip()) > 100:
                raise ValueError("Full name cannot exceed 100 characters")
            
            self.full_name = self.full_name.strip() if self.full_name.strip() else None
    
    def update_username(self, new_username: str) -> None:
        """
        Update the username with validation.
        
        Args:
            new_username: The new username
            
        Raises:
            ValueError: If the new username is invalid
        """
        old_username = self.username
        self.username = new_username
        
        try:
            self._validate_username()
            self.updated_at = datetime.utcnow()
        except ValueError:
            self.username = old_username  # Rollback on validation failure
            raise
    
    def update_email(self, new_email: str) -> None:
        """
        Update the email with validation.
        
        Args:
            new_email: The new email address
            
        Raises:
            ValueError: If the new email is invalid
        """
        old_email = self.email
        self.email = new_email
        
        try:
            self._validate_email()
            self.updated_at = datetime.utcnow()
        except ValueError:
            self.email = old_email  # Rollback on validation failure
            raise
    
    def update_password_hash(self, new_password_hash: str) -> None:
        """
        Update the password hash.
        
        Args:
            new_password_hash: The new hashed password
            
        Raises:
            ValueError: If the new password hash is invalid
        """
        old_password_hash = self.password_hash
        self.password_hash = new_password_hash
        
        try:
            self._validate_password_hash()
            self.updated_at = datetime.utcnow()
        except ValueError:
            self.password_hash = old_password_hash  # Rollback on validation failure
            raise
    
    def update_full_name(self, new_full_name: Optional[str]) -> None:
        """
        Update the full name with validation.
        
        Args:
            new_full_name: The new full name (can be None)
            
        Raises:
            ValueError: If the new full name is invalid
        """
        old_full_name = self.full_name
        self.full_name = new_full_name
        
        try:
            self._validate_full_name()
            self.updated_at = datetime.utcnow()
        except ValueError:
            self.full_name = old_full_name  # Rollback on validation failure
            raise
    
    def activate(self) -> None:
        """
        Activate the user account.
        
        Business rule: Only inactive users can be activated.
        """
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """
        Deactivate the user account.
        
        Business rule: Only active users can be deactivated.
        """
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()
    
    def make_superuser(self) -> None:
        """
        Grant superuser privileges to the user.
        
        Business rule: User must be active to become superuser.
        """
        if not self.is_active:
            raise ValueError("Cannot grant superuser privileges to inactive user")
        
        if not self.is_superuser:
            self.is_superuser = True
            self.updated_at = datetime.utcnow()
    
    def remove_superuser(self) -> None:
        """
        Remove superuser privileges from the user.
        """
        if self.is_superuser:
            self.is_superuser = False
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Convert the user to a dictionary representation.
        
        Note: Password hash is excluded for security reasons.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the user."""
        return (f"User(id={self.id}, username='{self.username}', email='{self.email}', "
                f"is_active={self.is_active}, is_superuser={self.is_superuser})")
