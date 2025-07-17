"""
Blog Post Repository Interface - Domain Layer

This module defines the abstract interface for blog post repository operations.
Following Clean Architecture and SOLID principles, this interface:
- Defines the contract for data persistence operations
- Is independent of any specific database or framework
- Allows for easy testing and implementation swapping
- Follows the Dependency Inversion Principle
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.blog_post import BlogPost


class BlogPostRepository(ABC):
    """
    Abstract repository interface for BlogPost entities.
    
    This interface defines all the operations needed to persist and retrieve
    blog posts without specifying the implementation details. This allows
    the domain layer to remain independent of infrastructure concerns.
    
    Following the Repository pattern and Dependency Inversion Principle,
    concrete implementations will be provided in the infrastructure layer.
    """
    
    @abstractmethod
    async def create(self, blog_post: BlogPost) -> BlogPost:
        """
        Create a new blog post in the repository.
        
        Args:
            blog_post: The BlogPost entity to create
            
        Returns:
            The created BlogPost entity with any repository-generated fields
            
        Raises:
            RepositoryError: If the blog post cannot be created
            DuplicateError: If a blog post with the same ID already exists
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, blog_post_id: UUID) -> Optional[BlogPost]:
        """
        Retrieve a blog post by its unique identifier.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            
        Returns:
            The BlogPost entity if found, None otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[BlogPost]:
        """
        Retrieve all blog posts with optional pagination.
        
        Args:
            limit: Maximum number of blog posts to return (default: 100)
            offset: Number of blog posts to skip (default: 0)
            
        Returns:
            List of BlogPost entities
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def update(self, blog_post: BlogPost) -> BlogPost:
        """
        Update an existing blog post in the repository.
        
        Args:
            blog_post: The BlogPost entity with updated data
            
        Returns:
            The updated BlogPost entity
            
        Raises:
            RepositoryError: If there's an error updating the blog post
            NotFoundError: If the blog post doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, blog_post_id: UUID) -> bool:
        """
        Delete a blog post from the repository.
        
        Args:
            blog_post_id: The unique identifier of the blog post to delete
            
        Returns:
            True if the blog post was deleted, False if it didn't exist
            
        Raises:
            RepositoryError: If there's an error deleting the blog post
        """
        pass
    
    @abstractmethod
    async def exists(self, blog_post_id: UUID) -> bool:
        """
        Check if a blog post exists in the repository.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            
        Returns:
            True if the blog post exists, False otherwise
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Get the total number of blog posts in the repository.
        
        Returns:
            Total number of blog posts
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def search_by_title(self, title_query: str, limit: int = 100) -> List[BlogPost]:
        """
        Search blog posts by title (case-insensitive partial match).
        
        Args:
            title_query: The search query for the title
            limit: Maximum number of results to return (default: 100)
            
        Returns:
            List of BlogPost entities matching the search criteria
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass
    
    @abstractmethod
    async def get_recent(self, limit: int = 10) -> List[BlogPost]:
        """
        Get the most recently created blog posts.
        
        Args:
            limit: Maximum number of recent posts to return (default: 10)
            
        Returns:
            List of BlogPost entities ordered by creation date (newest first)
            
        Raises:
            RepositoryError: If there's an error accessing the repository
        """
        pass


class BlogPostRepositoryError(Exception):
    """Base exception for blog post repository operations."""
    pass


class BlogPostNotFoundError(BlogPostRepositoryError):
    """Exception raised when a blog post is not found."""
    
    def __init__(self, blog_post_id: UUID):
        self.blog_post_id = blog_post_id
        super().__init__(f"Blog post with ID {blog_post_id} not found")


class DuplicateBlogPostError(BlogPostRepositoryError):
    """Exception raised when trying to create a blog post that already exists."""
    
    def __init__(self, blog_post_id: UUID):
        self.blog_post_id = blog_post_id
        super().__init__(f"Blog post with ID {blog_post_id} already exists")
