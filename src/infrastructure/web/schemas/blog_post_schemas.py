"""
Blog Post Pydantic Schemas - Infrastructure Layer

This module contains Pydantic models for blog post API request/response validation.
Following Clean Architecture principles, these schemas:
- Handle API data validation and serialization
- Convert between API formats and domain entities
- Provide clear API documentation through Pydantic
- Are independent of business logic
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class BlogPostCreateRequest(BaseModel):
    """Schema for creating a new blog post."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the blog post",
        example="My First Blog Post"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Content of the blog post",
        example="This is the content of my first blog post..."
    )
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()


class BlogPostUpdateRequest(BaseModel):
    """Schema for updating an existing blog post."""
    
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="New title of the blog post",
        example="Updated Blog Post Title"
    )
    content: Optional[str] = Field(
        None,
        min_length=1,
        description="New content of the blog post",
        example="This is the updated content..."
    )
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip() if v else v
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip() if v else v


class BlogPostSummaryResponse(BaseModel):
    """Schema for blog post summary (used in list endpoints)."""
    
    id: str = Field(
        ...,
        description="Unique identifier of the blog post",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    title: str = Field(
        ...,
        description="Title of the blog post",
        example="My First Blog Post"
    )
    created_at: datetime = Field(
        ...,
        description="When the blog post was created",
        example="2024-01-15T10:30:00Z"
    )
    updated_at: datetime = Field(
        ...,
        description="When the blog post was last updated",
        example="2024-01-15T10:30:00Z"
    )
    comment_count: int = Field(
        ...,
        description="Number of approved comments on this post",
        example=5
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BlogPostResponse(BaseModel):
    """Schema for full blog post response."""
    
    id: str = Field(
        ...,
        description="Unique identifier of the blog post",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    title: str = Field(
        ...,
        description="Title of the blog post",
        example="My First Blog Post"
    )
    content: str = Field(
        ...,
        description="Content of the blog post",
        example="This is the content of my first blog post..."
    )
    created_at: datetime = Field(
        ...,
        description="When the blog post was created",
        example="2024-01-15T10:30:00Z"
    )
    updated_at: datetime = Field(
        ...,
        description="When the blog post was last updated",
        example="2024-01-15T10:30:00Z"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BlogPostWithCommentsResponse(BaseModel):
    """Schema for blog post with its comments."""
    
    id: str = Field(
        ...,
        description="Unique identifier of the blog post",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    title: str = Field(
        ...,
        description="Title of the blog post",
        example="My First Blog Post"
    )
    content: str = Field(
        ...,
        description="Content of the blog post",
        example="This is the content of my first blog post..."
    )
    created_at: datetime = Field(
        ...,
        description="When the blog post was created",
        example="2024-01-15T10:30:00Z"
    )
    updated_at: datetime = Field(
        ...,
        description="When the blog post was last updated",
        example="2024-01-15T10:30:00Z"
    )
    comments: List['CommentResponse'] = Field(
        default_factory=list,
        description="List of approved comments on this post"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BlogPostListResponse(BaseModel):
    """Schema for paginated blog post list response."""
    
    posts: List[BlogPostSummaryResponse] = Field(
        ...,
        description="List of blog posts"
    )
    total: int = Field(
        ...,
        description="Total number of blog posts",
        example=25
    )
    limit: int = Field(
        ...,
        description="Maximum number of posts returned",
        example=10
    )
    offset: int = Field(
        ...,
        description="Number of posts skipped",
        example=0
    )


# Import CommentResponse to resolve forward reference
from .comment_schemas import CommentResponse
BlogPostWithCommentsResponse.model_rebuild()
