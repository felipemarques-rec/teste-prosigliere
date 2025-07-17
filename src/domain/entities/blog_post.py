"""
Blog Post Entity - Domain Layer

This module contains the BlogPost entity which represents the core business logic
for blog posts without any framework dependencies.

Following Clean Architecture principles, this entity contains:
- Business rules and validation logic
- Domain-specific behavior
- No dependencies on external frameworks or infrastructure
"""

from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class BlogPost:
    """
    BlogPost entity representing a blog post in the domain.
    
    This entity encapsulates the business rules for blog posts:
    - Title must be between 1 and 200 characters
    - Content must not be empty
    - Created and updated timestamps are managed automatically
    - Each post has a unique identifier
    
    Attributes:
        id: Unique identifier for the blog post
        title: Title of the blog post (1-200 characters)
        content: Content of the blog post (required)
        created_at: Timestamp when the post was created
        updated_at: Timestamp when the post was last updated
        comment_ids: List of comment IDs associated with this post
    """
    
    title: str
    content: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    comment_ids: List[UUID] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate the blog post data after initialization."""
        self._validate_title()
        self._validate_content()
    
    def _validate_title(self) -> None:
        """
        Validate the blog post title.
        
        Business Rules:
        - Title cannot be empty
        - Title cannot exceed 200 characters
        - Title must be a string
        
        Raises:
            ValueError: If title validation fails
        """
        if not isinstance(self.title, str):
            raise ValueError("Title must be a string")
        
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")
    
    def _validate_content(self) -> None:
        """
        Validate the blog post content.
        
        Business Rules:
        - Content cannot be empty
        - Content must be a string
        
        Raises:
            ValueError: If content validation fails
        """
        if not isinstance(self.content, str):
            raise ValueError("Content must be a string")
        
        if not self.content.strip():
            raise ValueError("Content cannot be empty")
    
    def update_title(self, new_title: str) -> None:
        """
        Update the blog post title with validation.
        
        Args:
            new_title: The new title for the blog post
            
        Raises:
            ValueError: If the new title is invalid
        """
        old_title = self.title
        self.title = new_title
        
        try:
            self._validate_title()
            self.updated_at = datetime.utcnow()
        except ValueError:
            self.title = old_title  # Rollback on validation failure
            raise
    
    def update_content(self, new_content: str) -> None:
        """
        Update the blog post content with validation.
        
        Args:
            new_content: The new content for the blog post
            
        Raises:
            ValueError: If the new content is invalid
        """
        old_content = self.content
        self.content = new_content
        
        try:
            self._validate_content()
            self.updated_at = datetime.utcnow()
        except ValueError:
            self.content = old_content  # Rollback on validation failure
            raise
    
    def add_comment_id(self, comment_id: UUID) -> None:
        """
        Add a comment ID to this blog post.
        
        Args:
            comment_id: UUID of the comment to associate with this post
            
        Raises:
            ValueError: If comment_id is not a UUID or already exists
        """
        if not isinstance(comment_id, UUID):
            raise ValueError("Comment ID must be a UUID")
        
        if comment_id in self.comment_ids:
            raise ValueError("Comment ID already exists for this post")
        
        self.comment_ids.append(comment_id)
        self.updated_at = datetime.utcnow()
    
    def remove_comment_id(self, comment_id: UUID) -> None:
        """
        Remove a comment ID from this blog post.
        
        Args:
            comment_id: UUID of the comment to remove from this post
            
        Raises:
            ValueError: If comment_id is not found
        """
        if comment_id not in self.comment_ids:
            raise ValueError("Comment ID not found for this post")
        
        self.comment_ids.remove(comment_id)
        self.updated_at = datetime.utcnow()
    
    def get_comment_count(self) -> int:
        """
        Get the number of comments associated with this blog post.
        
        Returns:
            Number of comments associated with this post
        """
        return len(self.comment_ids)
    
    def to_dict(self) -> dict:
        """
        Convert the blog post to a dictionary representation.
        
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
    
    def __str__(self) -> str:
        """String representation of the blog post."""
        return f"BlogPost(id={self.id}, title='{self.title[:50]}...', comments={self.get_comment_count()})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the blog post."""
        return (f"BlogPost(id={self.id}, title='{self.title}', "
                f"created_at={self.created_at}, comment_count={self.get_comment_count()})")
