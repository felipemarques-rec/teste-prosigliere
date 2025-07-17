"""
Comment Database Model - Infrastructure Layer

This module contains the SQLAlchemy model for comments.
Following Clean Architecture principles, this model:
- Handles database-specific concerns (tables, columns, relationships)
- Maps between domain entities and database records
- Is independent of business logic
- Provides conversion methods to/from domain entities
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ....domain.entities.comment import Comment

if TYPE_CHECKING:
    from .blog_post_model import BlogPostModel


class CommentModel(Base):
    """
    SQLAlchemy model for comments.
    
    This model represents the database table structure for comments
    and provides methods to convert between database records and domain entities.
    
    Table: comments
    """
    
    __tablename__ = "comments"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Comment fields
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    author_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Anonymous"
    )
    
    author_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default=""
    )
    
    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True  # Index for filtering approved comments
    )
    
    # Foreign key to blog post
    blog_post_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("blog_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Index for querying comments by blog post
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
    blog_post: Mapped["BlogPostModel"] = relationship(
        "BlogPostModel",
        back_populates="comments"
    )
    
    def __repr__(self) -> str:
        """String representation of the comment model."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<CommentModel(id={self.id}, author='{self.author_name}', content='{content_preview}')>"
    
    def to_entity(self) -> Comment:
        """
        Convert the database model to a domain entity.
        
        This method transforms the SQLAlchemy model into a domain entity,
        following the Clean Architecture principle of keeping domain logic
        separate from infrastructure concerns.
        
        Returns:
            Comment: Domain entity representation
        """
        # Create domain entity with database values
        comment = Comment.__new__(Comment)  # Create without calling __init__
        comment.id = self.id
        comment.content = self.content
        comment.blog_post_id = self.blog_post_id
        comment.author_name = self.author_name
        comment.author_email = self.author_email
        comment.created_at = self.created_at
        comment.updated_at = self.updated_at
        comment.is_approved = self.is_approved
        
        return comment
    
    @classmethod
    def from_entity(cls, entity: Comment) -> "CommentModel":
        """
        Create a database model from a domain entity.
        
        This method transforms a domain entity into a SQLAlchemy model
        for database persistence.
        
        Args:
            entity: Comment domain entity
            
        Returns:
            CommentModel: Database model representation
        """
        return cls(
            id=entity.id,
            content=entity.content,
            blog_post_id=entity.blog_post_id,
            author_name=entity.author_name,
            author_email=entity.author_email,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_approved=entity.is_approved
        )
    
    def update_from_entity(self, entity: Comment) -> None:
        """
        Update the database model from a domain entity.
        
        This method updates the existing database model with values
        from a domain entity, preserving the database-specific fields.
        
        Args:
            entity: Comment domain entity with updated values
        """
        self.content = entity.content
        self.author_name = entity.author_name
        self.author_email = entity.author_email
        self.updated_at = entity.updated_at
        self.is_approved = entity.is_approved
    
    def get_content_preview(self, max_length: int = 100) -> str:
        """
        Get a preview of the comment content.
        
        Args:
            max_length: Maximum length of the preview
            
        Returns:
            Truncated content with ellipsis if needed
        """
        if len(self.content) <= max_length:
            return self.content
        
        return self.content[:max_length].rstrip() + "..."
    
    def is_recent(self, hours: int = 24) -> bool:
        """
        Check if the comment was created recently.
        
        Args:
            hours: Number of hours to consider as "recent"
            
        Returns:
            True if the comment was created within the specified hours
        """
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.total_seconds() < (hours * 3600)
    
    def to_dict(self) -> dict:
        """
        Convert the model to a dictionary representation.
        
        Returns:
            Dictionary representation of the comment
        """
        return {
            'id': str(self.id),
            'content': self.content,
            'blog_post_id': str(self.blog_post_id),
            'author_name': self.author_name,
            'author_email': self.author_email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_approved': self.is_approved
        }
    
    def to_public_dict(self) -> dict:
        """
        Convert the model to a public dictionary representation.
        
        This excludes sensitive information like author email
        and is suitable for public API responses.
        
        Returns:
            Public dictionary representation of the comment
        """
        return {
            'id': str(self.id),
            'content': self.content,
            'author_name': self.author_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
