"""
Blog Post Database Model - Infrastructure Layer

This module contains the SQLAlchemy model for blog posts.
Following Clean Architecture principles, this model:
- Handles database-specific concerns (tables, columns, relationships)
- Maps between domain entities and database records
- Is independent of business logic
- Provides conversion methods to/from domain entities
"""

from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ....domain.entities.blog_post import BlogPost

if TYPE_CHECKING:
    from .comment_model import CommentModel


class BlogPostModel(Base):
    """
    SQLAlchemy model for blog posts.
    
    This model represents the database table structure for blog posts
    and provides methods to convert between database records and domain entities.
    
    Table: blog_posts
    """
    
    __tablename__ = "blog_posts"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Blog post fields
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True  # Index for search functionality
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        index=True  # Index for sorting by creation date
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    comments: Mapped[List["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="blog_post",
        cascade="all, delete-orphan",  # Delete comments when blog post is deleted
        lazy="selectin"  # Optimize loading of comments
    )
    
    def __repr__(self) -> str:
        """String representation of the blog post model."""
        return f"<BlogPostModel(id={self.id}, title='{self.title[:50]}...')>"
    
    def to_entity(self) -> BlogPost:
        """
        Convert the database model to a domain entity.
        
        This method transforms the SQLAlchemy model into a domain entity,
        following the Clean Architecture principle of keeping domain logic
        separate from infrastructure concerns.
        
        Returns:
            BlogPost: Domain entity representation
        """
        # Extract comment IDs from the relationship
        comment_ids = [comment.id for comment in self.comments] if self.comments else []
        
        # Create domain entity with database values
        blog_post = BlogPost.__new__(BlogPost)  # Create without calling __init__
        blog_post.id = self.id
        blog_post.title = self.title
        blog_post.content = self.content
        blog_post.created_at = self.created_at
        blog_post.updated_at = self.updated_at
        blog_post.comment_ids = comment_ids
        
        return blog_post
    
    @classmethod
    def from_entity(cls, entity: BlogPost) -> "BlogPostModel":
        """
        Create a database model from a domain entity.
        
        This method transforms a domain entity into a SQLAlchemy model
        for database persistence.
        
        Args:
            entity: BlogPost domain entity
            
        Returns:
            BlogPostModel: Database model representation
        """
        return cls(
            id=entity.id,
            title=entity.title,
            content=entity.content,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def update_from_entity(self, entity: BlogPost) -> None:
        """
        Update the database model from a domain entity.
        
        This method updates the existing database model with values
        from a domain entity, preserving the database-specific fields.
        
        Args:
            entity: BlogPost domain entity with updated values
        """
        self.title = entity.title
        self.content = entity.content
        self.updated_at = entity.updated_at
    
    def get_comment_count(self) -> int:
        """
        Get the number of comments associated with this blog post.
        
        Returns:
            Number of comments
        """
        return len(self.comments) if self.comments else 0
    
    def get_approved_comment_count(self) -> int:
        """
        Get the number of approved comments associated with this blog post.
        
        Returns:
            Number of approved comments
        """
        if not self.comments:
            return 0
        
        return sum(1 for comment in self.comments if comment.is_approved)
    
    def to_dict(self) -> dict:
        """
        Convert the model to a dictionary representation.
        
        Returns:
            Dictionary representation of the blog post
        """
        return {
            'id': str(self.id),
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'comment_count': self.get_comment_count()
        }
    
    def to_summary_dict(self) -> dict:
        """
        Convert the model to a summary dictionary representation.
        
        This is useful for list endpoints where full content is not needed.
        
        Returns:
            Summary dictionary representation of the blog post
        """
        return {
            'id': str(self.id),
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'comment_count': self.get_approved_comment_count()
        }
