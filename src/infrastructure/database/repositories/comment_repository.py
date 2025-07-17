"""
SQLAlchemy Comment Repository Implementation - Infrastructure Layer

This module contains the concrete implementation of the CommentRepository interface
using SQLAlchemy for data persistence.
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities.comment import Comment
from ....domain.repositories.comment_repository import (
    CommentRepository,
    CommentRepositoryError,
    CommentNotFoundError,
    DuplicateCommentError
)
from ..models.comment_model import CommentModel


logger = logging.getLogger(__name__)


class CommentRepositoryImpl(CommentRepository):
    """SQLAlchemy implementation of the CommentRepository interface."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, comment: Comment) -> Comment:
        try:
            existing = await self._session.get(CommentModel, comment.id)
            if existing:
                raise DuplicateCommentError(comment.id)
            
            db_comment = CommentModel.from_entity(comment)
            self._session.add(db_comment)
            await self._session.flush()
            await self._session.refresh(db_comment)
            
            return db_comment.to_entity()
        except DuplicateCommentError:
            raise
        except Exception as e:
            raise CommentRepositoryError(f"Failed to create comment: {e}")
    
    async def get_by_id(self, comment_id: UUID) -> Optional[Comment]:
        try:
            db_comment = await self._session.get(CommentModel, comment_id)
            return db_comment.to_entity() if db_comment else None
        except Exception as e:
            raise CommentRepositoryError(f"Failed to retrieve comment: {e}")
    
    async def get_by_blog_post_id(self, blog_post_id: UUID, limit: int = 100, offset: int = 0) -> List[Comment]:
        try:
            stmt = select(CommentModel).where(
                CommentModel.blog_post_id == blog_post_id
            ).order_by(CommentModel.created_at.desc()).limit(limit).offset(offset)
            
            result = await self._session.execute(stmt)
            db_comments = result.scalars().all()
            return [db_comment.to_entity() for db_comment in db_comments]
        except Exception as e:
            raise CommentRepositoryError(f"Failed to retrieve comments: {e}")
    
    async def get_approved_by_blog_post_id(self, blog_post_id: UUID, limit: int = 100, offset: int = 0) -> List[Comment]:
        try:
            stmt = select(CommentModel).where(
                CommentModel.blog_post_id == blog_post_id,
                CommentModel.is_approved == True
            ).order_by(CommentModel.created_at.desc()).limit(limit).offset(offset)
            
            result = await self._session.execute(stmt)
            db_comments = result.scalars().all()
            return [db_comment.to_entity() for db_comment in db_comments]
        except Exception as e:
            raise CommentRepositoryError(f"Failed to retrieve approved comments: {e}")
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Comment]:
        try:
            stmt = select(CommentModel).order_by(CommentModel.created_at.desc()).limit(limit).offset(offset)
            result = await self._session.execute(stmt)
            db_comments = result.scalars().all()
            return [db_comment.to_entity() for db_comment in db_comments]
        except Exception as e:
            raise CommentRepositoryError(f"Failed to retrieve comments: {e}")
    
    async def update(self, comment: Comment) -> Comment:
        try:
            db_comment = await self._session.get(CommentModel, comment.id)
            if not db_comment:
                raise CommentNotFoundError(comment.id)
            
            db_comment.update_from_entity(comment)
            await self._session.flush()
            await self._session.refresh(db_comment)
            
            return db_comment.to_entity()
        except CommentNotFoundError:
            raise
        except Exception as e:
            raise CommentRepositoryError(f"Failed to update comment: {e}")
    
    async def delete(self, comment_id: UUID) -> bool:
        try:
            db_comment = await self._session.get(CommentModel, comment_id)
            if not db_comment:
                return False
            
            await self._session.delete(db_comment)
            await self._session.flush()
            return True
        except Exception as e:
            raise CommentRepositoryError(f"Failed to delete comment: {e}")
    
    async def delete_by_blog_post_id(self, blog_post_id: UUID) -> int:
        try:
            stmt = delete(CommentModel).where(CommentModel.blog_post_id == blog_post_id)
            result = await self._session.execute(stmt)
            return result.rowcount
        except Exception as e:
            raise CommentRepositoryError(f"Failed to delete comments: {e}")
    
    async def exists(self, comment_id: UUID) -> bool:
        try:
            stmt = select(CommentModel.id).where(CommentModel.id == comment_id)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise CommentRepositoryError(f"Failed to check comment existence: {e}")
    
    async def count_by_blog_post_id(self, blog_post_id: UUID) -> int:
        try:
            stmt = select(func.count(CommentModel.id)).where(CommentModel.blog_post_id == blog_post_id)
            result = await self._session.execute(stmt)
            return result.scalar()
        except Exception as e:
            raise CommentRepositoryError(f"Failed to count comments: {e}")
    
    async def count_approved_by_blog_post_id(self, blog_post_id: UUID) -> int:
        try:
            stmt = select(func.count(CommentModel.id)).where(
                CommentModel.blog_post_id == blog_post_id,
                CommentModel.is_approved == True
            )
            result = await self._session.execute(stmt)
            return result.scalar()
        except Exception as e:
            raise CommentRepositoryError(f"Failed to count approved comments: {e}")
    
    async def get_recent(self, limit: int = 10) -> List[Comment]:
        try:
            stmt = select(CommentModel).order_by(CommentModel.created_at.desc()).limit(limit)
            result = await self._session.execute(stmt)
            db_comments = result.scalars().all()
            return [db_comment.to_entity() for db_comment in db_comments]
        except Exception as e:
            raise CommentRepositoryError(f"Failed to retrieve recent comments: {e}")
    
    async def get_pending_approval(self, limit: int = 100, offset: int = 0) -> List[Comment]:
        try:
            stmt = select(CommentModel).where(
                CommentModel.is_approved == False
            ).order_by(CommentModel.created_at.desc()).limit(limit).offset(offset)
            
            result = await self._session.execute(stmt)
            db_comments = result.scalars().all()
            return [db_comment.to_entity() for db_comment in db_comments]
        except Exception as e:
            raise CommentRepositoryError(f"Failed to retrieve pending comments: {e}")
