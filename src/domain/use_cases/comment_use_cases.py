"""
Comment Use Cases - Domain Layer

This module contains the application business rules for comment operations.
Following Clean Architecture principles, these use cases:
- Orchestrate the flow of data to and from entities
- Coordinate between different repositories
- Implement application-specific business rules
- Are independent of frameworks and external concerns
"""

from typing import List, Optional
from uuid import UUID

from ..entities.comment import Comment
from ..entities.blog_post import BlogPost
from ..repositories.comment_repository import (
    CommentRepository,
    CommentNotFoundError,
    DuplicateCommentError
)
from ..repositories.blog_post_repository import (
    BlogPostRepository,
    BlogPostNotFoundError
)


class CommentUseCases:
    """
    Use cases for comment operations.
    
    This class implements the application business rules for managing comments.
    It coordinates between the comment and blog post repositories to provide
    high-level operations while maintaining business logic integrity.
    
    Following the Single Responsibility Principle, this class focuses solely
    on comment-related business operations.
    """
    
    def __init__(
        self,
        comment_repository: CommentRepository,
        blog_post_repository: BlogPostRepository
    ):
        """
        Initialize the comment use cases.
        
        Args:
            comment_repository: Repository for comment persistence
            blog_post_repository: Repository for blog post persistence
        """
        self._comment_repository = comment_repository
        self._blog_post_repository = blog_post_repository
    
    async def create_comment(
        self,
        blog_post_id: UUID,
        content: str,
        author_name: str = "Anonymous",
        author_email: str = ""
    ) -> Comment:
        """
        Create a new comment for a blog post.
        
        Business Rules:
        - Blog post must exist before adding a comment
        - Content must be valid according to entity rules
        - Comment ID must be unique
        - Comments are approved by default (can be changed for moderation)
        
        Args:
            blog_post_id: ID of the blog post to comment on
            content: Content of the comment
            author_name: Name of the comment author (optional)
            author_email: Email of the comment author (optional)
            
        Returns:
            The created Comment entity
            
        Raises:
            BlogPostNotFoundError: If the blog post doesn't exist
            ValueError: If content or author information is invalid
            DuplicateCommentError: If a comment with the same ID already exists
        """
        # Verify that the blog post exists
        blog_post = await self._blog_post_repository.get_by_id(blog_post_id)
        if blog_post is None:
            raise BlogPostNotFoundError(blog_post_id)
        
        # Create the comment entity (validation happens in entity)
        comment = Comment(
            content=content,
            blog_post_id=blog_post_id,
            author_name=author_name,
            author_email=author_email
        )
        
        # Check if comment already exists (unlikely with UUID, but good practice)
        if await self._comment_repository.exists(comment.id):
            raise DuplicateCommentError(comment.id)
        
        # Persist the comment
        created_comment = await self._comment_repository.create(comment)
        
        # Update the blog post's comment list (business rule)
        blog_post.add_comment_id(created_comment.id)
        await self._blog_post_repository.update(blog_post)
        
        return created_comment
    
    async def get_comment_by_id(self, comment_id: UUID) -> Comment:
        """
        Retrieve a comment by its ID.
        
        Args:
            comment_id: Unique identifier of the comment
            
        Returns:
            The Comment entity
            
        Raises:
            CommentNotFoundError: If the comment doesn't exist
        """
        comment = await self._comment_repository.get_by_id(comment_id)
        
        if comment is None:
            raise CommentNotFoundError(comment_id)
        
        return comment
    
    async def get_comments_for_blog_post(
        self,
        blog_post_id: UUID,
        approved_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Comment]:
        """
        Retrieve comments for a specific blog post.
        
        Business Rule: By default, only approved comments are returned for public viewing.
        
        Args:
            blog_post_id: Unique identifier of the blog post
            approved_only: Whether to return only approved comments (default: True)
            limit: Maximum number of comments to return
            offset: Number of comments to skip
            
        Returns:
            List of Comment entities
            
        Raises:
            BlogPostNotFoundError: If the blog post doesn't exist
        """
        # Verify that the blog post exists
        if not await self._blog_post_repository.exists(blog_post_id):
            raise BlogPostNotFoundError(blog_post_id)
        
        if approved_only:
            return await self._comment_repository.get_approved_by_blog_post_id(
                blog_post_id, limit=limit, offset=offset
            )
        else:
            return await self._comment_repository.get_by_blog_post_id(
                blog_post_id, limit=limit, offset=offset
            )
    
    async def update_comment(
        self,
        comment_id: UUID,
        content: str = None,
        author_name: str = None,
        author_email: str = None
    ) -> Comment:
        """
        Update an existing comment.
        
        Business Rules:
        - Comment must exist
        - Only provided fields are updated
        - Updated timestamp is automatically managed
        
        Args:
            comment_id: Unique identifier of the comment
            content: New content (optional)
            author_name: New author name (optional)
            author_email: New author email (optional)
            
        Returns:
            The updated Comment entity
            
        Raises:
            CommentNotFoundError: If the comment doesn't exist
            ValueError: If the new content or author information is invalid
        """
        # Get the existing comment
        comment = await self.get_comment_by_id(comment_id)
        
        # Update fields if provided
        if content is not None:
            comment.update_content(content)
        
        if author_name is not None or author_email is not None:
            comment.update_author_info(name=author_name, email=author_email)
        
        # Persist the changes
        return await self._comment_repository.update(comment)
    
    async def approve_comment(self, comment_id: UUID) -> Comment:
        """
        Approve a comment for public display.
        
        Business Rule: Only approved comments are shown to the public.
        
        Args:
            comment_id: Unique identifier of the comment
            
        Returns:
            The approved Comment entity
            
        Raises:
            CommentNotFoundError: If the comment doesn't exist
        """
        comment = await self.get_comment_by_id(comment_id)
        comment.approve()
        return await self._comment_repository.update(comment)
    
    async def reject_comment(self, comment_id: UUID) -> Comment:
        """
        Reject a comment (hide from public display).
        
        Business Rule: Rejected comments are not shown to the public.
        
        Args:
            comment_id: Unique identifier of the comment
            
        Returns:
            The rejected Comment entity
            
        Raises:
            CommentNotFoundError: If the comment doesn't exist
        """
        comment = await self.get_comment_by_id(comment_id)
        comment.reject()
        return await self._comment_repository.update(comment)
    
    async def delete_comment(self, comment_id: UUID) -> bool:
        """
        Delete a comment.
        
        Business Rule: When a comment is deleted, it's also removed from the blog post's comment list.
        
        Args:
            comment_id: Unique identifier of the comment
            
        Returns:
            True if the comment was deleted, False if it didn't exist
        """
        # Get the comment to find its blog post
        try:
            comment = await self.get_comment_by_id(comment_id)
        except CommentNotFoundError:
            return False
        
        # Remove comment from blog post's comment list
        blog_post = await self._blog_post_repository.get_by_id(comment.blog_post_id)
        if blog_post:
            try:
                blog_post.remove_comment_id(comment_id)
                await self._blog_post_repository.update(blog_post)
            except ValueError:
                # Comment ID not in blog post's list, continue with deletion
                pass
        
        # Delete the comment
        return await self._comment_repository.delete(comment_id)
    
    async def get_recent_comments(self, limit: int = 10) -> List[Comment]:
        """
        Get the most recently created comments.
        
        Args:
            limit: Maximum number of recent comments to return
            
        Returns:
            List of Comment entities ordered by creation date (newest first)
        """
        return await self._comment_repository.get_recent(limit=limit)
    
    async def get_pending_comments(self, limit: int = 100, offset: int = 0) -> List[Comment]:
        """
        Get comments that are pending approval.
        
        This is useful for moderation workflows.
        
        Args:
            limit: Maximum number of comments to return
            offset: Number of comments to skip
            
        Returns:
            List of Comment entities that are not approved
        """
        return await self._comment_repository.get_pending_approval(limit=limit, offset=offset)
    
    async def get_comment_statistics(self) -> dict:
        """
        Get statistics about comments.
        
        Returns:
            Dictionary containing comment statistics
        """
        recent_comments = await self._comment_repository.get_recent(limit=5)
        pending_comments = await self._comment_repository.get_pending_approval(limit=1)
        
        return {
            'recent_comments_count': len(recent_comments),
            'pending_approval_count': len(pending_comments),
            'recent_comments': [comment.to_dict() for comment in recent_comments]
        }
    
    async def moderate_comments_batch(
        self,
        comment_ids: List[UUID],
        action: str
    ) -> List[Comment]:
        """
        Perform batch moderation actions on multiple comments.
        
        Args:
            comment_ids: List of comment IDs to moderate
            action: Action to perform ('approve' or 'reject')
            
        Returns:
            List of moderated Comment entities
            
        Raises:
            ValueError: If action is not valid
            CommentNotFoundError: If any comment doesn't exist
        """
        if action not in ['approve', 'reject']:
            raise ValueError("Action must be 'approve' or 'reject'")
        
        moderated_comments = []
        
        for comment_id in comment_ids:
            if action == 'approve':
                comment = await self.approve_comment(comment_id)
            else:  # reject
                comment = await self.reject_comment(comment_id)
            
            moderated_comments.append(comment)
        
        return moderated_comments


class CommentUseCaseError(Exception):
    """Base exception for comment use case operations."""
    pass


class InvalidCommentDataError(CommentUseCaseError):
    """Exception raised when comment data is invalid."""
    pass


class CommentModerationError(CommentUseCaseError):
    """Exception raised when comment moderation fails."""
    pass
