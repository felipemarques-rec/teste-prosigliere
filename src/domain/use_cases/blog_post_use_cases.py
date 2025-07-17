"""
Blog Post Use Cases - Domain Layer

This module contains the application business rules for blog post operations.
Following Clean Architecture principles, these use cases:
- Orchestrate the flow of data to and from entities
- Coordinate between different repositories
- Implement application-specific business rules
- Are independent of frameworks and external concerns
"""

from typing import List, Optional
from uuid import UUID

from ..entities.blog_post import BlogPost
from ..entities.comment import Comment
from ..repositories.blog_post_repository import (
    BlogPostRepository,
    BlogPostNotFoundError,
    DuplicateBlogPostError
)
from ..repositories.comment_repository import CommentRepository


class BlogPostUseCases:
    """
    Use cases for blog post operations.
    
    This class implements the application business rules for managing blog posts.
    It coordinates between the blog post and comment repositories to provide
    high-level operations while maintaining business logic integrity.
    
    Following the Single Responsibility Principle, this class focuses solely
    on blog post-related business operations.
    """
    
    def __init__(
        self,
        blog_post_repository: BlogPostRepository,
        comment_repository: CommentRepository
    ):
        """
        Initialize the blog post use cases.
        
        Args:
            blog_post_repository: Repository for blog post persistence
            comment_repository: Repository for comment persistence
        """
        self._blog_post_repository = blog_post_repository
        self._comment_repository = comment_repository
    
    async def create_blog_post(self, title: str, content: str) -> BlogPost:
        """
        Create a new blog post.
        
        Business Rules:
        - Title and content must be valid according to entity rules
        - Blog post ID must be unique
        
        Args:
            title: Title of the blog post
            content: Content of the blog post
            
        Returns:
            The created BlogPost entity
            
        Raises:
            ValueError: If title or content are invalid
            DuplicateBlogPostError: If a blog post with the same ID already exists
        """
        # Create the blog post entity (validation happens in entity)
        blog_post = BlogPost(title=title, content=content)
        
        # Check if blog post already exists (unlikely with UUID, but good practice)
        if await self._blog_post_repository.exists(blog_post.id):
            raise DuplicateBlogPostError(blog_post.id)
        
        # Persist the blog post
        return await self._blog_post_repository.create(blog_post)
    
    async def get_blog_post_by_id(self, blog_post_id: UUID) -> BlogPost:
        """
        Retrieve a blog post by its ID.
        
        Args:
            blog_post_id: Unique identifier of the blog post
            
        Returns:
            The BlogPost entity
            
        Raises:
            BlogPostNotFoundError: If the blog post doesn't exist
        """
        blog_post = await self._blog_post_repository.get_by_id(blog_post_id)
        
        if blog_post is None:
            raise BlogPostNotFoundError(blog_post_id)
        
        return blog_post
    
    async def get_blog_post_with_comments(self, blog_post_id: UUID) -> tuple[BlogPost, List[Comment]]:
        """
        Retrieve a blog post with its associated comments.
        
        Business Rule: Only approved comments are returned for public viewing.
        
        Args:
            blog_post_id: Unique identifier of the blog post
            
        Returns:
            Tuple containing the BlogPost entity and list of approved Comment entities
            
        Raises:
            BlogPostNotFoundError: If the blog post doesn't exist
        """
        # Get the blog post
        blog_post = await self.get_blog_post_by_id(blog_post_id)
        
        # Get approved comments for the blog post
        comments = await self._comment_repository.get_approved_by_blog_post_id(blog_post_id)
        
        return blog_post, comments
    
    async def get_all_blog_posts(self, limit: int = 100, offset: int = 0) -> List[BlogPost]:
        """
        Retrieve all blog posts with pagination.
        
        Args:
            limit: Maximum number of blog posts to return
            offset: Number of blog posts to skip
            
        Returns:
            List of BlogPost entities
        """
        return await self._blog_post_repository.get_all(limit=limit, offset=offset)
    
    async def get_blog_posts_summary(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """
        Get a summary of all blog posts including comment counts.
        
        This use case implements the business logic for the GET /api/posts endpoint,
        which requires blog posts with their comment counts.
        
        Args:
            limit: Maximum number of blog posts to return
            offset: Number of blog posts to skip
            
        Returns:
            List of dictionaries containing blog post summaries with comment counts
        """
        blog_posts = await self._blog_post_repository.get_all(limit=limit, offset=offset)
        
        # Build summary with comment counts
        summaries = []
        for blog_post in blog_posts:
            comment_count = await self._comment_repository.count_approved_by_blog_post_id(blog_post.id)
            
            summary = {
                'id': str(blog_post.id),
                'title': blog_post.title,
                'created_at': blog_post.created_at.isoformat(),
                'updated_at': blog_post.updated_at.isoformat(),
                'comment_count': comment_count
            }
            summaries.append(summary)
        
        return summaries
    
    async def update_blog_post(self, blog_post_id: UUID, title: str = None, content: str = None) -> BlogPost:
        """
        Update an existing blog post.
        
        Business Rules:
        - Blog post must exist
        - Only provided fields are updated
        - Updated timestamp is automatically managed
        
        Args:
            blog_post_id: Unique identifier of the blog post
            title: New title (optional)
            content: New content (optional)
            
        Returns:
            The updated BlogPost entity
            
        Raises:
            BlogPostNotFoundError: If the blog post doesn't exist
            ValueError: If the new title or content are invalid
        """
        # Get the existing blog post
        blog_post = await self.get_blog_post_by_id(blog_post_id)
        
        # Update fields if provided
        if title is not None:
            blog_post.update_title(title)
        
        if content is not None:
            blog_post.update_content(content)
        
        # Persist the changes
        return await self._blog_post_repository.update(blog_post)
    
    async def delete_blog_post(self, blog_post_id: UUID) -> bool:
        """
        Delete a blog post and all its associated comments.
        
        Business Rule: When a blog post is deleted, all its comments are also deleted.
        
        Args:
            blog_post_id: Unique identifier of the blog post
            
        Returns:
            True if the blog post was deleted, False if it didn't exist
        """
        # Check if blog post exists
        if not await self._blog_post_repository.exists(blog_post_id):
            return False
        
        # Delete all comments associated with the blog post
        await self._comment_repository.delete_by_blog_post_id(blog_post_id)
        
        # Delete the blog post
        return await self._blog_post_repository.delete(blog_post_id)
    
    async def search_blog_posts(self, title_query: str, limit: int = 100) -> List[BlogPost]:
        """
        Search blog posts by title.
        
        Args:
            title_query: Search query for the title
            limit: Maximum number of results to return
            
        Returns:
            List of BlogPost entities matching the search criteria
        """
        return await self._blog_post_repository.search_by_title(title_query, limit=limit)
    
    async def get_recent_blog_posts(self, limit: int = 10) -> List[BlogPost]:
        """
        Get the most recently created blog posts.
        
        Args:
            limit: Maximum number of recent posts to return
            
        Returns:
            List of BlogPost entities ordered by creation date (newest first)
        """
        return await self._blog_post_repository.get_recent(limit=limit)
    
    async def get_blog_post_statistics(self) -> dict:
        """
        Get statistics about blog posts.
        
        Returns:
            Dictionary containing blog post statistics
        """
        total_posts = await self._blog_post_repository.count()
        recent_posts = await self._blog_post_repository.get_recent(limit=5)
        
        return {
            'total_posts': total_posts,
            'recent_posts_count': len(recent_posts),
            'recent_posts': [post.to_dict() for post in recent_posts]
        }


class BlogPostUseCaseError(Exception):
    """Base exception for blog post use case operations."""
    pass


class InvalidBlogPostDataError(BlogPostUseCaseError):
    """Exception raised when blog post data is invalid."""
    pass
