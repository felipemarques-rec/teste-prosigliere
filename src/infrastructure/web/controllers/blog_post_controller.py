"""
Blog Post Controller - Infrastructure Layer

This module contains the FastAPI route handlers for blog post operations.
Following Clean Architecture principles, this controller:
- Handles HTTP requests and responses
- Validates input using Pydantic schemas
- Delegates business logic to use cases
- Converts between API schemas and domain entities
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities.user import User
from ....domain.use_cases.blog_post_use_cases import BlogPostUseCases
from ....domain.use_cases.comment_use_cases import CommentUseCases
from ....domain.repositories.blog_post_repository import BlogPostNotFoundError
from ....infrastructure.database.database import get_database_session
from ....infrastructure.database.repositories.blog_post_repository import BlogPostRepositoryImpl
from ....infrastructure.database.repositories.comment_repository import CommentRepositoryImpl
from ....infrastructure.web.controllers.auth_controller import get_current_active_user
from ..schemas.blog_post_schemas import (
    BlogPostCreateRequest,
    BlogPostUpdateRequest,
    BlogPostResponse,
    BlogPostSummaryResponse,
    BlogPostWithCommentsResponse,
    BlogPostListResponse
)
from ..schemas.comment_schemas import CommentResponse


router = APIRouter(prefix="/api/posts", tags=["Blog Posts"])


async def get_blog_post_use_cases(
    session: AsyncSession = Depends(get_database_session)
) -> BlogPostUseCases:
    """Dependency to get blog post use cases."""
    blog_post_repo = BlogPostRepositoryImpl(session)
    comment_repo = CommentRepositoryImpl(session)
    return BlogPostUseCases(blog_post_repo, comment_repo)


async def get_comment_use_cases(
    session: AsyncSession = Depends(get_database_session)
) -> CommentUseCases:
    """Dependency to get comment use cases."""
    comment_repo = CommentRepositoryImpl(session)
    blog_post_repo = BlogPostRepositoryImpl(session)
    return CommentUseCases(comment_repo, blog_post_repo)


@router.get(
    "",
    response_model=List[BlogPostSummaryResponse],
    summary="Get all blog posts",
    description="Retrieve a list of all blog posts with their comment counts"
)
async def get_all_blog_posts(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    use_cases: BlogPostUseCases = Depends(get_blog_post_use_cases)
):
    """
    Get all blog posts with pagination.
    
    Returns a list of blog post summaries including:
    - Basic post information (id, title, timestamps)
    - Number of approved comments for each post
    """
    try:
        summaries = await use_cases.get_blog_posts_summary(limit=limit, offset=offset)
        
        return [
            BlogPostSummaryResponse(
                id=summary["id"],
                title=summary["title"],
                created_at=summary["created_at"],
                updated_at=summary["updated_at"],
                comment_count=summary["comment_count"]
            )
            for summary in summaries
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve blog posts: {str(e)}"
        )


@router.post(
    "",
    response_model=BlogPostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new blog post",
    description="Create a new blog post with title and content (requires authentication)"
)
async def create_blog_post(
    request: BlogPostCreateRequest,
    current_user: User = Depends(get_current_active_user),
    use_cases: BlogPostUseCases = Depends(get_blog_post_use_cases)
):
    """
    Create a new blog post.
    
    Requires:
    - title: String between 1-200 characters
    - content: Non-empty string
    
    Returns the created blog post with generated ID and timestamps.
    """
    try:
        blog_post = await use_cases.create_blog_post(
            title=request.title,
            content=request.content
        )
        
        return BlogPostResponse(
            id=str(blog_post.id),
            title=blog_post.title,
            content=blog_post.content,
            created_at=blog_post.created_at,
            updated_at=blog_post.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create blog post: {str(e)}"
        )


@router.get(
    "/{post_id}",
    response_model=BlogPostWithCommentsResponse,
    summary="Get a specific blog post",
    description="Retrieve a specific blog post by ID with its approved comments"
)
async def get_blog_post(
    post_id: UUID,
    use_cases: BlogPostUseCases = Depends(get_blog_post_use_cases)
):
    """
    Get a specific blog post by ID.
    
    Returns:
    - Full blog post details
    - List of approved comments associated with the post
    
    Raises 404 if the blog post is not found.
    """
    try:
        blog_post, comments = await use_cases.get_blog_post_with_comments(post_id)
        
        comment_responses = [
            CommentResponse(
                id=str(comment.id),
                content=comment.content,
                author_name=comment.author_name,
                created_at=comment.created_at,
                updated_at=comment.updated_at
            )
            for comment in comments
        ]
        
        return BlogPostWithCommentsResponse(
            id=str(blog_post.id),
            title=blog_post.title,
            content=blog_post.content,
            created_at=blog_post.created_at,
            updated_at=blog_post.updated_at,
            comments=comment_responses
        )
    except BlogPostNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog post with ID {post_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve blog post: {str(e)}"
        )


@router.put(
    "/{post_id}",
    response_model=BlogPostResponse,
    summary="Update a blog post",
    description="Update an existing blog post's title and/or content (requires authentication)"
)
async def update_blog_post(
    post_id: UUID,
    request: BlogPostUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    use_cases: BlogPostUseCases = Depends(get_blog_post_use_cases)
):
    """
    Update an existing blog post.
    
    Can update:
    - title: New title (optional)
    - content: New content (optional)
    
    At least one field must be provided.
    Returns the updated blog post.
    """
    try:
        if not request.title and not request.content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field (title or content) must be provided"
            )
        
        blog_post = await use_cases.update_blog_post(
            blog_post_id=post_id,
            title=request.title,
            content=request.content
        )
        
        return BlogPostResponse(
            id=str(blog_post.id),
            title=blog_post.title,
            content=blog_post.content,
            created_at=blog_post.created_at,
            updated_at=blog_post.updated_at
        )
    except BlogPostNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog post with ID {post_id} not found"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update blog post: {str(e)}"
        )


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a blog post",
    description="Delete a blog post and all its associated comments (requires authentication)"
)
async def delete_blog_post(
    post_id: UUID,
    current_user: User = Depends(get_current_active_user),
    use_cases: BlogPostUseCases = Depends(get_blog_post_use_cases)
):
    """
    Delete a blog post.
    
    This will also delete all comments associated with the blog post.
    Returns 204 No Content on success, 404 if the post doesn't exist.
    """
    try:
        deleted = await use_cases.delete_blog_post(post_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post with ID {post_id} not found"
            )
        
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete blog post: {str(e)}"
        )
