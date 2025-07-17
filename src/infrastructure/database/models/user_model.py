"""
User Database Model - Infrastructure Layer

This module contains the SQLAlchemy model for users.
Following Clean Architecture principles, this model:
- Handles database-specific concerns (tables, columns, relationships)
- Maps between domain entities and database records
- Is independent of business logic
- Provides conversion methods to/from domain entities
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from ....domain.entities.user import User


class UserModel(Base):
    """
    SQLAlchemy model for users.
    
    This model represents the database table structure for users
    and provides methods to convert between database records and domain entities.
    
    Table: users
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # User fields
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True  # Index for login queries
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True  # Index for login queries
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True  # Index for filtering active users
    )
    
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True  # Index for admin queries
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
    
    def __repr__(self) -> str:
        """String representation of the user model."""
        return f"<UserModel(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_entity(self) -> User:
        """
        Convert the database model to a domain entity.
        
        This method transforms the SQLAlchemy model into a domain entity,
        following the Clean Architecture principle of keeping domain logic
        separate from infrastructure concerns.
        
        Returns:
            User: Domain entity representation
        """
        # Create domain entity with database values
        user = User.__new__(User)  # Create without calling __init__
        user.id = self.id
        user.username = self.username
        user.email = self.email
        user.password_hash = self.password_hash
        user.full_name = self.full_name
        user.is_active = self.is_active
        user.is_superuser = self.is_superuser
        user.created_at = self.created_at
        user.updated_at = self.updated_at
        
        return user
    
    @classmethod
    def from_entity(cls, entity: User) -> "UserModel":
        """
        Create a database model from a domain entity.
        
        This method transforms a domain entity into a SQLAlchemy model
        for database persistence.
        
        Args:
            entity: User domain entity
            
        Returns:
            UserModel: Database model representation
        """
        return cls(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def update_from_entity(self, entity: User) -> None:
        """
        Update the database model from a domain entity.
        
        This method updates the existing database model with values
        from a domain entity, preserving the database-specific fields.
        
        Args:
            entity: User domain entity with updated values
        """
        self.username = entity.username
        self.email = entity.email
        self.password_hash = entity.password_hash
        self.full_name = entity.full_name
        self.is_active = entity.is_active
        self.is_superuser = entity.is_superuser
        self.updated_at = entity.updated_at
    
    def to_dict(self) -> dict:
        """
        Convert the model to a dictionary representation.
        
        Note: Password hash is excluded for security reasons.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_public_dict(self) -> dict:
        """
        Convert the model to a public dictionary representation.
        
        This excludes sensitive information and is suitable for public API responses.
        
        Returns:
            Public dictionary representation of the user
        """
        return {
            'id': str(self.id),
            'username': self.username,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat()
        }
