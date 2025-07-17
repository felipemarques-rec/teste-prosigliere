"""
Comment Controller - Infrastructure Layer

This module contains the FastAPI route handlers for comment operations.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.use_cases.comment_use_cases import CommentUseCases
from ....domain.repositories.comment_repository import CommentNotFoundError
from ....domain.repositories.blog_post_repository import BlogPostNotFoundError
from ....infrastructure.database.database import get_database_session
from ....infrastructure.database.repositories.comment_repository import CommentRepositoryImpl
from ....infrastructure.database.repositories.blog_post_repository import BlogPostRepositoryImpl
from ..schemas.comment_schemas import CommentCreateRequest, CommentResponse


router = APIRouter(prefix="/api/posts", tags=["Comments"])


async def get_comment_use_cases(
    session: AsyncSession = Depends(get_database_session)
) -> CommentUseCases:
    """Dependency to get comment use cases."""
    comment_repo = CommentRepositoryImpl(session)
    blog_post_repo = BlogPostRepositoryImpl(session)
    return CommentUseCases(comment_repo, blog_post_repo)


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a blog post",
    description="Create a new comment for a specific blog post"
)
async def create_comment(
    post_id: UUID,
    request: CommentCreateRequest,
    use_cases: CommentUseCases = Depends(get_comment_use_cases)
):
    """
    Add a new comment to a blog post.
    
    Requires:
    - content: Comment content (1-1000 characters)
    - author_name: Author name (optional, defaults to "Anonymous")
    - author_email: Author email (optional)
    
    Returns the created comment.
    """
    try:
        comment = await use_cases.create_comment(
            blog_post_id=post_id,
            content=request.content,
            author_name=request.author_name or "Anonymous",
            author_email=request.author_email or ""
        )
        
        return CommentResponse(
            id=str(comment.id),
            content=comment.content,
            author_name=comment.author_name,
            created_at=comment.created_at,
            updated_at=comment.updated_at
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
            detail=f"Failed to create comment: {str(e)}"
        )
