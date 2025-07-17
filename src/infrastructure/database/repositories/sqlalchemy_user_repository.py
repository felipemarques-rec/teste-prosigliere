"""
SQLAlchemy User Repository Implementation - Infrastructure Layer

This module contains the concrete implementation of the UserRepository interface
using SQLAlchemy for data persistence.
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities.user import User
from ....domain.repositories.user_repository import (
    UserRepository,
    UserRepositoryError,
    UserNotFoundError,
    DuplicateUserError
)
from ..models.user_model import UserModel


logger = logging.getLogger(__name__)


class UserRepositoryImpl(UserRepository):
    """SQLAlchemy implementation of the UserRepository interface."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, user: User) -> User:
        try:
            # Check if user already exists by ID, username, or email
            existing_id = await self._session.get(UserModel, user.id)
            if existing_id:
                raise DuplicateUserError(str(user.id), "id")
            
            if await self.exists_by_username(user.username):
                raise DuplicateUserError(user.username, "username")
            
            if await self.exists_by_email(user.email):
                raise DuplicateUserError(user.email, "email")
            
            db_user = UserModel.from_entity(user)
            self._session.add(db_user)
            await self._session.flush()
            await self._session.refresh(db_user)
            
            return db_user.to_entity()
        except (DuplicateUserError):
            raise
        except Exception as e:
            raise UserRepositoryError(f"Failed to create user: {e}")
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            db_user = await self._session.get(UserModel, user_id)
            return db_user.to_entity() if db_user else None
        except Exception as e:
            raise UserRepositoryError(f"Failed to retrieve user: {e}")
    
    async def get_by_username(self, username: str) -> Optional[User]:
        try:
            stmt = select(UserModel).where(UserModel.username == username)
            result = await self._session.execute(stmt)
            db_user = result.scalar_one_or_none()
            return db_user.to_entity() if db_user else None
        except Exception as e:
            raise UserRepositoryError(f"Failed to retrieve user by username: {e}")
    
    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            stmt = select(UserModel).where(UserModel.email == email.lower())
            result = await self._session.execute(stmt)
            db_user = result.scalar_one_or_none()
            return db_user.to_entity() if db_user else None
        except Exception as e:
            raise UserRepositoryError(f"Failed to retrieve user by email: {e}")
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        try:
            stmt = select(UserModel).order_by(UserModel.created_at.desc()).limit(limit).offset(offset)
            result = await self._session.execute(stmt)
            db_users = result.scalars().all()
            return [db_user.to_entity() for db_user in db_users]
        except Exception as e:
            raise UserRepositoryError(f"Failed to retrieve users: {e}")
    
    async def get_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        try:
            stmt = select(UserModel).where(
                UserModel.is_active == True
            ).order_by(UserModel.created_at.desc()).limit(limit).offset(offset)
            
            result = await self._session.execute(stmt)
            db_users = result.scalars().all()
            return [db_user.to_entity() for db_user in db_users]
        except Exception as e:
            raise UserRepositoryError(f"Failed to retrieve active users: {e}")
    
    async def update(self, user: User) -> User:
        try:
            db_user = await self._session.get(UserModel, user.id)
            if not db_user:
                raise UserNotFoundError(str(user.id))
            
            db_user.update_from_entity(user)
            await self._session.flush()
            await self._session.refresh(db_user)
            
            return db_user.to_entity()
        except UserNotFoundError:
            raise
        except Exception as e:
            raise UserRepositoryError(f"Failed to update user: {e}")
    
    async def delete(self, user_id: UUID) -> bool:
        try:
            db_user = await self._session.get(UserModel, user_id)
            if not db_user:
                return False
            
            await self._session.delete(db_user)
            await self._session.flush()
            return True
        except Exception as e:
            raise UserRepositoryError(f"Failed to delete user: {e}")
    
    async def exists_by_username(self, username: str) -> bool:
        try:
            stmt = select(UserModel.id).where(UserModel.username == username)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise UserRepositoryError(f"Failed to check username existence: {e}")
    
    async def exists_by_email(self, email: str) -> bool:
        try:
            stmt = select(UserModel.id).where(UserModel.email == email.lower())
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise UserRepositoryError(f"Failed to check email existence: {e}")
    
    async def exists(self, user_id: UUID) -> bool:
        try:
            stmt = select(UserModel.id).where(UserModel.id == user_id)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise UserRepositoryError(f"Failed to check user existence: {e}")
    
    async def count(self) -> int:
        try:
            stmt = select(func.count(UserModel.id))
            result = await self._session.execute(stmt)
            return result.scalar()
        except Exception as e:
            raise UserRepositoryError(f"Failed to count users: {e}")
    
    async def count_active(self) -> int:
        try:
            stmt = select(func.count(UserModel.id)).where(UserModel.is_active == True)
            result = await self._session.execute(stmt)
            return result.scalar()
        except Exception as e:
            raise UserRepositoryError(f"Failed to count active users: {e}")
    
    async def search_by_username(self, username_query: str, limit: int = 100) -> List[User]:
        try:
            stmt = select(UserModel).where(
                UserModel.username.ilike(f"%{username_query}%")
            ).order_by(UserModel.created_at.desc()).limit(limit)
            
            result = await self._session.execute(stmt)
            db_users = result.scalars().all()
            return [db_user.to_entity() for db_user in db_users]
        except Exception as e:
            raise UserRepositoryError(f"Failed to search users: {e}")
    
    async def get_recent(self, limit: int = 10) -> List[User]:
        try:
            stmt = select(UserModel).order_by(UserModel.created_at.desc()).limit(limit)
            result = await self._session.execute(stmt)
            db_users = result.scalars().all()
            return [db_user.to_entity() for db_user in db_users]
        except Exception as e:
            raise UserRepositoryError(f"Failed to retrieve recent users: {e}")
