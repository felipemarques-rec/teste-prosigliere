"""
User Repository Interface - Domain Layer

This module defines the abstract interface for user repository operations.
Following Clean Architecture and SOLID principles, this interface:
- Defines the contract for data persistence operations
- Is independent of any specific database or framework
- Allows for easy testing and implementation swapping
- Follows the Dependency Inversion Principle
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.user import User


class UserRepository(ABC):
    """
    Abstract repository interface for User entities.
    
    This interface defines all the operations needed to persist and retrieve
    users without specifying the implementation details. This allows
    the domain layer to remain independent of infrastructure concerns.
    
    Following the Repository pattern and Dependency Inversion Principle,
    concrete implementations will be provided in the infrastructure layer.
    """
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create a new user in the repository.
        
        Args:
            user: The User entity to create
            
        Returns:
            The created User entity with any repository-generated fields
            
        Raises:
            RepositoryError: If the user cannot be created
            DuplicateError: If a user with the same ID, username, or email already exists
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by their unique identifier.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            The User entity if found, None otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.
        
        Args:
            username: The username of the user
            
        Returns:
            The User entity if found, None otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        
        Args:
            email: The email address of the user
            
        Returns:
            The User entity if found, None otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        Retrieve all users with optional pagination.
        
        Args:
            limit: Maximum number of users to return (default: 100)
            offset: Number of users to skip (default: 0)
            
        Returns:
            List of User entities
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        Retrieve all active users with optional pagination.
        
        Args:
            limit: Maximum number of users to return (default: 100)
            offset: Number of users to skip (default: 0)
            
        Returns:
            List of active User entities
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Update an existing user in the repository.
        
        Args:
            user: The User entity with updated data
            
        Returns:
            The updated User entity
            
        Raises:
            RepositoryError: If there's an error updating the user
            NotFoundError: If the user doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user from the repository.
        
        Args:
            user_id: The unique identifier of the user to delete
            
        Returns:
            True if the user was deleted, False if it didn't exist
            
        Raises:
            RepositoryError: If there's an error deleting the user
        """
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """
        Check if a user exists with the given username.
        
        Args:
            username: The username to check
            
        Returns:
            True if a user exists with this username, False otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists with the given email.
        
        Args:
            email: The email to check
            
        Returns:
            True if a user exists with this email, False otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def exists(self, user_id: UUID) -> bool:
        """
        Check if a user exists in the repository.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            True if the user exists, False otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Get the total number of users in the repository.
        
        Returns:
            Total number of users
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def count_active(self) -> int:
        """
        Get the total number of active users in the repository.
        
        Returns:
            Total number of active users
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def search_by_username(self, username_query: str, limit: int = 100) -> List[User]:
        """
        Search users by username (case-insensitive partial match).
        
        Args:
            username_query: The search query for the username
            limit: Maximum number of results to return (default: 100)
            
        Returns:
            List of User entities matching the search criteria
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_recent(self, limit: int = 10) -> List[User]:
        """
        Get the most recently created users.
        
        Args:
            limit: Maximum number of recent users to return (default: 10)
            
        Returns:
            List of User entities ordered by creation date (newest first)
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass


class UserRepositoryError(Exception):
    """Base exception for user repository operations."""
    pass


class UserNotFoundError(UserRepositoryError):
    """Exception raised when a user is not found."""
    
    def __init__(self, identifier: str, field: str = "id"):
        self.identifier = identifier
        self.field = field
        super().__init__(f"User with {field} '{identifier}' not found")


class DuplicateUserError(UserRepositoryError):
    """Exception raised when trying to create a user that already exists."""
    
    def __init__(self, identifier: str, field: str = "id"):
        self.identifier = identifier
        self.field = field
        super().__init__(f"User with {field} '{identifier}' already exists")
