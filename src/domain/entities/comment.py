"""
Comment Entity - Domain Layer

This module contains the Comment entity which represents the core business logic
for comments without any framework dependencies.

Following Clean Architecture principles, this entity contains:
- Business rules and validation logic
- Domain-specific behavior
- No dependencies on external frameworks or infrastructure
"""

from datetime import datetime
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Comment:
    """
    Comment entity representing a comment in the domain.
    
    This entity encapsulates the business rules for comments:
    - Content must not be empty and cannot exceed 1000 characters
    - Each comment must be associated with a blog post
    - Created and updated timestamps are managed automatically
    - Each comment has a unique identifier
    
    Attributes:
        id: Unique identifier for the comment
        content: Content of the comment (1-1000 characters)
        blog_post_id: ID of the blog post this comment belongs to
        author_name: Name of the comment author (optional for now)
        author_email: Email of the comment author (optional for now)
        created_at: Timestamp when the comment was created
        updated_at: Timestamp when the comment was last updated
        is_approved: Whether the comment is approved for display
    """
    
    content: str
    blog_post_id: UUID
    id: UUID = field(default_factory=uuid4)
    author_name: str = field(default="Anonymous")
    author_email: str = field(default="")
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_approved: bool = field(default=True)
    
    def __post_init__(self):
        """Validate the comment data after initialization."""
        self._validate_content()
        self._validate_blog_post_id()
        self._validate_author_name()
        self._validate_author_email()
    
    def _validate_content(self) -> None:
        """
        Validate the comment content.
        
        Business Rules:
        - Content cannot be empty
        - Content cannot exceed 1000 characters
        - Content must be a string
        
        Raises:
            ValueError: If content validation fails
        """
        if not isinstance(self.content, str):
            raise ValueError("Content must be a string")
        
        if not self.content.strip():
            raise ValueError("Content cannot be empty")
        
        if len(self.content) > 1000:
            raise ValueError("Content cannot exceed 1000 characters")
    
    def _validate_blog_post_id(self) -> None:
        """
        Validate the blog post ID.
        
        Business Rules:
        - Blog post ID must be a valid UUID
        - Blog post ID cannot be None
        
        Raises:
            ValueError: If blog post ID validation fails
        """
        if not isinstance(self.blog_post_id, UUID):
            raise ValueError("Blog post ID must be a UUID")
    
    def _validate_author_name(self) -> None:
        """
        Validate the author name.
        
        Business Rules:
        - Author name must be a string
        - Author name cannot exceed 100 characters
        
        Raises:
            ValueError: If author name validation fails
        """
        if not isinstance(self.author_name, str):
            raise ValueError("Author name must be a string")
        
        if len(self.author_name) > 100:
            raise ValueError("Author name cannot exceed 100 characters")
    
    def _validate_author_email(self) -> None:
        """
        Validate the author email.
        
        Business Rules:
        - Author email must be a string
        - Author email cannot exceed 255 characters
        - If provided, email should contain @ symbol (basic validation)
        
        Raises:
            ValueError: If author email validation fails
        """
        if not isinstance(self.author_email, str):
            raise ValueError("Author email must be a string")
        
        if len(self.author_email) > 255:
            raise ValueError("Author email cannot exceed 255 characters")
        
        if self.author_email and "@" not in self.author_email:
            raise ValueError("Author email must be a valid email address")
    
    def update_content(self, new_content: str) -> None:
        """
        Update the comment content with validation.
        
        Args:
            new_content: The new content for the comment
            
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
    
    def update_author_info(self, name: str = None, email: str = None) -> None:
        """
        Update the author information with validation.
        
        Args:
            name: New author name (optional)
            email: New author email (optional)
            
        Raises:
            ValueError: If the new author information is invalid
        """
        old_name = self.author_name
        old_email = self.author_email
        
        try:
            if name is not None:
                self.author_name = name
                self._validate_author_name()
            
            if email is not None:
                self.author_email = email
                self._validate_author_email()
            
            self.updated_at = datetime.utcnow()
            
        except ValueError:
            # Rollback on validation failure
            self.author_name = old_name
            self.author_email = old_email
            raise
    
    def approve(self) -> None:
        """
        Approve the comment for display.
        
        This method implements the business rule for comment moderation.
        """
        if not self.is_approved:
            self.is_approved = True
            self.updated_at = datetime.utcnow()
    
    def reject(self) -> None:
        """
        Reject the comment (hide from display).
        
        This method implements the business rule for comment moderation.
        """
        if self.is_approved:
            self.is_approved = False
            self.updated_at = datetime.utcnow()
    
    def is_recent(self, hours: int = 24) -> bool:
        """
        Check if the comment was created recently.
        
        Args:
            hours: Number of hours to consider as "recent" (default: 24)
            
        Returns:
            True if the comment was created within the specified hours
        """
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.total_seconds() < (hours * 3600)
    
    def get_content_preview(self, max_length: int = 100) -> str:
        """
        Get a preview of the comment content.
        
        Args:
            max_length: Maximum length of the preview (default: 100)
            
        Returns:
            Truncated content with ellipsis if needed
        """
        if len(self.content) <= max_length:
            return self.content
        
        return self.content[:max_length].rstrip() + "..."
    
    def to_dict(self) -> dict:
        """
        Convert the comment to a dictionary representation.
        
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
    
    def __str__(self) -> str:
        """String representation of the comment."""
        preview = self.get_content_preview(50)
        return f"Comment(id={self.id}, author='{self.author_name}', content='{preview}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the comment."""
        return (f"Comment(id={self.id}, blog_post_id={self.blog_post_id}, "
                f"author='{self.author_name}', created_at={self.created_at}, "
                f"approved={self.is_approved})")
