"""
Comment Repository Interface - Domain Layer

This module defines the abstract interface for comment repository operations.
Following Clean Architecture and SOLID principles, this interface:
- Defines the contract for data persistence operations
- Is independent of any specific database or framework
- Allows for easy testing and implementation swapping
- Follows the Dependency Inversion Principle
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.comment import Comment


class CommentRepository(ABC):
    """
    Abstract repository interface for Comment entities.
    
    This interface defines all the operations needed to persist and retrieve
    comments without specifying the implementation details. This allows
    the domain layer to remain independent of infrastructure concerns.
    
    Following the Repository pattern and Dependency Inversion Principle,
    concrete implementations will be provided in the infrastructure layer.
    """
    
    @abstractmethod
    async def create(self, comment: Comment) -> Comment:
        """
        Create a new comment in the repository.
        
        Args:
            comment: The Comment entity to create
            
        Returns:
            The created Comment entity with any repository-generated fields
            
        Raises:
            RepositoryError: If the comment cannot be created
            DuplicateError: If a comment with the same ID already exists
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """
        Retrieve a comment by its unique identifier.
        
        Args:
            comment_id: The unique identifier of the comment
            
        Returns:
            The Comment entity if found, None otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_by_blog_post_id(self, blog_post_id: UUID, limit: int = 100, offset: int = 0) -> List[Comment]:
        """
        Retrieve all comments for a specific blog post.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            limit: Maximum number of comments to return (default: 100)
            offset: Number of comments to skip (default: 0)
            
        Returns:
            List of Comment entities for the specified blog post
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_approved_by_blog_post_id(self, blog_post_id: UUID, limit: int = 100, offset: int = 0) -> List[Comment]:
        """
        Retrieve all approved comments for a specific blog post.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            limit: Maximum number of comments to return (default: 100)
            offset: Number of comments to skip (default: 0)
            
        Returns:
            List of approved Comment entities for the specified blog post
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Comment]:
        """
        Retrieve all comments with optional pagination.
        
        Args:
            limit: Maximum number of comments to return (default: 100)
            offset: Number of comments to skip (default: 0)
            
        Returns:
            List of Comment entities
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def update(self, comment: Comment) -> Comment:
        """
        Update an existing comment in the repository.
        
        Args:
            comment: The Comment entity with updated data
            
        Returns:
            The updated Comment entity
            
        Raises:
            RepositoryError: If there's an error updating the comment
            NotFoundError: If the comment doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, comment_id: UUID) -> bool:
        """
        Delete a comment from the repository.
        
        Args:
            comment_id: The unique identifier of the comment to delete
            
        Returns:
            True if the comment was deleted, False if it didn't exist
            
        Raises:
            RepositoryError: If there's an error deleting the comment
        """
        pass
    
    @abstractmethod
    async def delete_by_blog_post_id(self, blog_post_id: UUID) -> int:
        """
        Delete all comments for a specific blog post.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            
        Returns:
            Number of comments deleted
            
        Raises:
            RepositoryError: If there's an error deleting the comments
        """
        pass
    
    @abstractmethod
    async def exists(self, comment_id: UUID) -> bool:
        """
        Check if a comment exists in the repository.
        
        Args:
            comment_id: The unique identifier of the comment
            
        Returns:
            True if the comment exists, False otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def count_by_blog_post_id(self, blog_post_id: UUID) -> int:
        """
        Get the total number of comments for a specific blog post.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            
        Returns:
            Total number of comments for the blog post
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def count_approved_by_blog_post_id(self, blog_post_id: UUID) -> int:
        """
        Get the total number of approved comments for a specific blog post.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            
        Returns:
            Total number of approved comments for the blog post
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_recent(self, limit: int = 10) -> List[Comment]:
        """
        Get the most recently created comments.
        
        Args:
            limit: Maximum number of recent comments to return (default: 10)
            
        Returns:
            List of Comment entities ordered by creation date (newest first)
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_pending_approval(self, limit: int = 100, offset: int = 0) -> List[Comment]:
        """
        Get comments that are pending approval.
        
        Args:
            limit: Maximum number of comments to return (default: 100)
            offset: Number of comments to skip (default: 0)
            
        Returns:
            List of Comment entities that are not approved
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass


class CommentRepositoryError(Exception):
    """Base exception for comment repository operations."""
    pass


class CommentNotFoundError(CommentRepositoryError):
    """Exception raised when a comment is not found."""
    
    def __init__(self, comment_id: UUID):
        self.comment_id = comment_id
        super().__init__(f"Comment with ID {comment_id} not found")


class DuplicateCommentError(CommentRepositoryError):
    """Exception raised when trying to create a comment that already exists."""
    
    def __init__(self, comment_id: UUID):
        self.comment_id = comment_id
        super().__init__(f"Comment with ID {comment_id} already exists")
