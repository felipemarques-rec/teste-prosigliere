"""
Comment Pydantic Schemas - Infrastructure Layer

This module contains Pydantic models for comment API request/response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class CommentCreateRequest(BaseModel):
    """Schema for creating a new comment."""
    
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Content of the comment",
        example="This is a great blog post!"
    )
    author_name: Optional[str] = Field(
        "Anonymous",
        max_length=100,
        description="Name of the comment author",
        example="John Doe"
    )
    author_email: Optional[str] = Field(
        "",
        max_length=255,
        description="Email of the comment author",
        example="john@example.com"
    )
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()
    
    @validator('author_name')
    def validate_author_name(cls, v):
        if v and not v.strip():
            raise ValueError('Author name cannot be whitespace only')
        return v.strip() if v else "Anonymous"
    
    @validator('author_email')
    def validate_author_email(cls, v):
        if v and v.strip() and "@" not in v:
            raise ValueError('Author email must be a valid email address')
        return v.strip() if v else ""


class CommentResponse(BaseModel):
    """Schema for comment response."""
    
    id: str = Field(
        ...,
        description="Unique identifier of the comment",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    content: str = Field(
        ...,
        description="Content of the comment",
        example="This is a great blog post!"
    )
    author_name: str = Field(
        ...,
        description="Name of the comment author",
        example="John Doe"
    )
    created_at: datetime = Field(
        ...,
        description="When the comment was created",
        example="2024-01-15T10:30:00Z"
    )
    updated_at: datetime = Field(
        ...,
        description="When the comment was last updated",
        example="2024-01-15T10:30:00Z"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CommentUpdateRequest(BaseModel):
    """Schema for updating an existing comment."""
    
    content: Optional[str] = Field(
        None,
        min_length=1,
        max_length=1000,
        description="New content of the comment",
        example="This is an updated comment!"
    )
    author_name: Optional[str] = Field(
        None,
        max_length=100,
        description="New author name",
        example="Jane Doe"
    )
    author_email: Optional[str] = Field(
        None,
        max_length=255,
        description="New author email",
        example="jane@example.com"
    )
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip() if v else v
    
    @validator('author_name')
    def validate_author_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Author name cannot be whitespace only')
        return v.strip() if v else v
    
    @validator('author_email')
    def validate_author_email(cls, v):
        if v is not None and v.strip() and "@" not in v:
            raise ValueError('Author email must be a valid email address')
        return v.strip() if v else v
