"""
SQLAlchemy Blog Post Repository Implementation - Infrastructure Layer

This module contains the concrete implementation of the BlogPostRepository interface
using SQLAlchemy for data persistence. Following Clean Architecture principles:
- Implements the repository interface defined in the domain layer
- Handles all database-specific operations
- Converts between domain entities and database models
- Provides error handling and logging
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....domain.entities.blog_post import BlogPost
from ....domain.repositories.blog_post_repository import (
    BlogPostRepository,
    BlogPostRepositoryError,
    BlogPostNotFoundError,
    DuplicateBlogPostError
)
from ..models.blog_post_model import BlogPostModel


logger = logging.getLogger(__name__)


class BlogPostRepositoryImpl(BlogPostRepository):
    """
    SQLAlchemy implementation of the BlogPostRepository interface.
    
    This class provides concrete implementations for all blog post repository
    operations using SQLAlchemy ORM for database interactions.
    
    Following the Repository pattern, this class:
    - Encapsulates database access logic
    - Converts between domain entities and database models
    - Handles database-specific errors
    - Provides logging for debugging and monitoring
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self._session = session
    
    async def create(self, blog_post: BlogPost) -> BlogPost:
        """
        Create a new blog post in the database.
        
        Args:
            blog_post: The BlogPost entity to create
            
        Returns:
            The created BlogPost entity
            
        Raises:
            DuplicateBlogPostError: If a blog post with the same ID already exists
            BlogPostRepositoryError: If there's an error creating the blog post
        """
        try:
            logger.debug(f"Creating blog post with ID: {blog_post.id}")
            
            # Check if blog post already exists
            existing = await self._session.get(BlogPostModel, blog_post.id)
            if existing:
                raise DuplicateBlogPostError(blog_post.id)
            
            # Create database model from domain entity
            db_blog_post = BlogPostModel.from_entity(blog_post)
            
            # Add to session and flush to get any database-generated values
            self._session.add(db_blog_post)
            await self._session.flush()
            await self._session.refresh(db_blog_post)
            
            logger.info(f"Successfully created blog post: {blog_post.id}")
            return db_blog_post.to_entity()
            
        except DuplicateBlogPostError:
            raise
        except Exception as e:
            logger.error(f"Error creating blog post {blog_post.id}: {e}")
            raise BlogPostRepositoryError(f"Failed to create blog post: {e}")
    
    async def get_by_id(self, blog_post_id: UUID) -> Optional[BlogPost]:
        """
        Retrieve a blog post by its unique identifier.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            
        Returns:
            The BlogPost entity if found, None otherwise
            
        Raises:
            BlogPostRepositoryError: If there's an error accessing the database
        """
        try:
            logger.debug(f"Retrieving blog post with ID: {blog_post_id}")
            
            # Query with eager loading of comments for complete entity
            stmt = select(BlogPostModel).options(
                selectinload(BlogPostModel.comments)
            ).where(BlogPostModel.id == blog_post_id)
            
            result = await self._session.execute(stmt)
            db_blog_post = result.scalar_one_or_none()
            
            if db_blog_post:
                logger.debug(f"Found blog post: {blog_post_id}")
                return db_blog_post.to_entity()
            
            logger.debug(f"Blog post not found: {blog_post_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving blog post {blog_post_id}: {e}")
            raise BlogPostRepositoryError(f"Failed to retrieve blog post: {e}")
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[BlogPost]:
        """
        Retrieve all blog posts with optional pagination.
        
        Args:
            limit: Maximum number of blog posts to return
            offset: Number of blog posts to skip
            
        Returns:
            List of BlogPost entities
            
        Raises:
            BlogPostRepositoryError: If there's an error accessing the database
        """
        try:
            logger.debug(f"Retrieving blog posts with limit={limit}, offset={offset}")
            
            stmt = select(BlogPostModel).options(
                selectinload(BlogPostModel.comments)
            ).order_by(BlogPostModel.created_at.desc()).limit(limit).offset(offset)
            
            result = await self._session.execute(stmt)
            db_blog_posts = result.scalars().all()
            
            blog_posts = [db_blog_post.to_entity() for db_blog_post in db_blog_posts]
            
            logger.debug(f"Retrieved {len(blog_posts)} blog posts")
            return blog_posts
            
        except Exception as e:
            logger.error(f"Error retrieving blog posts: {e}")
            raise BlogPostRepositoryError(f"Failed to retrieve blog posts: {e}")
    
    async def update(self, blog_post: BlogPost) -> BlogPost:
        """
        Update an existing blog post in the database.
        
        Args:
            blog_post: The BlogPost entity with updated data
            
        Returns:
            The updated BlogPost entity
            
        Raises:
            BlogPostNotFoundError: If the blog post doesn't exist
            BlogPostRepositoryError: If there's an error updating the blog post
        """
        try:
            logger.debug(f"Updating blog post with ID: {blog_post.id}")
            
            # Get existing blog post
            db_blog_post = await self._session.get(BlogPostModel, blog_post.id)
            if not db_blog_post:
                raise BlogPostNotFoundError(blog_post.id)
            
            # Update with new values
            db_blog_post.update_from_entity(blog_post)
            
            # Flush to apply changes and refresh to get updated values
            await self._session.flush()
            await self._session.refresh(db_blog_post)
            
            logger.info(f"Successfully updated blog post: {blog_post.id}")
            return db_blog_post.to_entity()
            
        except BlogPostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating blog post {blog_post.id}: {e}")
            raise BlogPostRepositoryError(f"Failed to update blog post: {e}")
    
    async def delete(self, blog_post_id: UUID) -> bool:
        """
        Delete a blog post from the database.
        
        Args:
            blog_post_id: The unique identifier of the blog post to delete
            
        Returns:
            True if the blog post was deleted, False if it didn't exist
            
        Raises:
            BlogPostRepositoryError: If there's an error deleting the blog post
        """
        try:
            logger.debug(f"Deleting blog post with ID: {blog_post_id}")
            
            # Get the blog post to delete
            db_blog_post = await self._session.get(BlogPostModel, blog_post_id)
            if not db_blog_post:
                logger.debug(f"Blog post not found for deletion: {blog_post_id}")
                return False
            
            # Delete the blog post (cascade will handle comments)
            await self._session.delete(db_blog_post)
            await self._session.flush()
            
            logger.info(f"Successfully deleted blog post: {blog_post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting blog post {blog_post_id}: {e}")
            raise BlogPostRepositoryError(f"Failed to delete blog post: {e}")
    
    async def exists(self, blog_post_id: UUID) -> bool:
        """
        Check if a blog post exists in the database.
        
        Args:
            blog_post_id: The unique identifier of the blog post
            
        Returns:
            True if the blog post exists, False otherwise
            
        Raises:
            BlogPostRepositoryError: If there's an error accessing the database
        """
        try:
            logger.debug(f"Checking existence of blog post: {blog_post_id}")
            
            stmt = select(BlogPostModel.id).where(BlogPostModel.id == blog_post_id)
            result = await self._session.execute(stmt)
            exists = result.scalar_one_or_none() is not None
            
            logger.debug(f"Blog post {blog_post_id} exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking blog post existence {blog_post_id}: {e}")
            raise BlogPostRepositoryError(f"Failed to check blog post existence: {e}")
    
    async def count(self) -> int:
        """
        Get the total number of blog posts in the database.
        
        Returns:
            Total number of blog posts
            
        Raises:
            BlogPostRepositoryError: If there's an error accessing the database
        """
        try:
            logger.debug("Counting total blog posts")
            
            stmt = select(func.count(BlogPostModel.id))
            result = await self._session.execute(stmt)
            count = result.scalar()
            
            logger.debug(f"Total blog posts count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting blog posts: {e}")
            raise BlogPostRepositoryError(f"Failed to count blog posts: {e}")
    
    async def search_by_title(self, title_query: str, limit: int = 100) -> List[BlogPost]:
        """
        Search blog posts by title (case-insensitive partial match).
        
        Args:
            title_query: The search query for the title
            limit: Maximum number of results to return
            
        Returns:
            List of BlogPost entities matching the search criteria
            
        Raises:
            BlogPostRepositoryError: If there's an error accessing the database
        """
        try:
            logger.debug(f"Searching blog posts by title: '{title_query}'")
            
            # Case-insensitive partial match
            stmt = select(BlogPostModel).options(
                selectinload(BlogPostModel.comments)
            ).where(
                BlogPostModel.title.ilike(f"%{title_query}%")
            ).order_by(BlogPostModel.created_at.desc()).limit(limit)
            
            result = await self._session.execute(stmt)
            db_blog_posts = result.scalars().all()
            
            blog_posts = [db_blog_post.to_entity() for db_blog_post in db_blog_posts]
            
            logger.debug(f"Found {len(blog_posts)} blog posts matching title search")
            return blog_posts
            
        except Exception as e:
            logger.error(f"Error searching blog posts by title '{title_query}': {e}")
            raise BlogPostRepositoryError(f"Failed to search blog posts: {e}")
    
    async def get_recent(self, limit: int = 10) -> List[BlogPost]:
        """
        Get the most recently created blog posts.
        
        Args:
            limit: Maximum number of recent posts to return
            
        Returns:
            List of BlogPost entities ordered by creation date (newest first)
            
        Raises:
            BlogPostRepositoryError: If there's an error accessing the database
        """
        try:
            logger.debug(f"Retrieving {limit} most recent blog posts")
            
            stmt = select(BlogPostModel).options(
                selectinload(BlogPostModel.comments)
            ).order_by(BlogPostModel.created_at.desc()).limit(limit)
            
            result = await self._session.execute(stmt)
            db_blog_posts = result.scalars().all()
            
            blog_posts = [db_blog_post.to_entity() for db_blog_post in db_blog_posts]
            
            logger.debug(f"Retrieved {len(blog_posts)} recent blog posts")
            return blog_posts
            
        except Exception as e:
            logger.error(f"Error retrieving recent blog posts: {e}")
            raise BlogPostRepositoryError(f"Failed to retrieve recent blog posts: {e}")
