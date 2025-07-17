"""
Database Configuration - Infrastructure Layer

This module contains the database configuration and session management.
Following Clean Architecture principles, this is part of the infrastructure layer
that provides concrete implementations for data persistence.

Key features:
- SQLAlchemy async engine configuration
- Database session management
- Connection pooling
- Health check functionality
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from pydantic_settings import BaseSettings


logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """
    Database configuration settings.
    
    Uses Pydantic settings for environment variable management
    with validation and type conversion.
    """
    database_url: str = "postgresql+asyncpg://blog_user:9649d919b@localhost:5432/blog_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    echo_sql: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    This provides a common base for all database models
    and enables SQLAlchemy's declarative mapping.
    """
    pass


class DatabaseManager:
    """
    Database manager for handling connections and sessions.
    
    This class encapsulates all database-related operations including:
    - Engine creation and configuration
    - Session management
    - Connection health checks
    - Graceful shutdown
    
    Following the Singleton pattern to ensure single database connection pool.
    """
    
    def __init__(self, settings: DatabaseSettings = None):
        """
        Initialize the database manager.
        
        Args:
            settings: Database configuration settings
        """
        self.settings = settings or DatabaseSettings()
        self.engine = None
        self.session_factory = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Initialize the database engine and session factory.
        
        This method should be called during application startup.
        """
        if self._initialized:
            return
        
        logger.info("Initializing database connection...")
        
        # Create async engine with connection pooling
        self.engine = create_async_engine(
            self.settings.database_url,
            echo=self.settings.echo_sql,
            pool_size=self.settings.database_pool_size,
            max_overflow=self.settings.database_max_overflow,
            pool_timeout=self.settings.database_pool_timeout,
            pool_recycle=self.settings.database_pool_recycle,
            pool_pre_ping=True,  # Validate connections before use
        )
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )
        
        self._initialized = True
        logger.info("Database connection initialized successfully")
    
    async def create_tables(self) -> None:
        """
        Create all database tables.
        
        This method should be called during application startup
        or as part of database migrations.
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info("Creating database tables...")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    
    async def drop_tables(self) -> None:
        """
        Drop all database tables.
        
        WARNING: This will delete all data. Use with caution.
        """
        if not self._initialized:
            await self.initialize()
        
        logger.warning("Dropping all database tables...")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.warning("All database tables dropped")
    
    async def health_check(self) -> bool:
        """
        Perform a database health check.
        
        Returns:
            True if database is healthy, False otherwise
        """
        if not self._initialized:
            return False
        
        try:
            async with self.session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session.
        
        This is an async context manager that provides a database session
        with automatic cleanup and error handling.
        
        Yields:
            AsyncSession: Database session
            
        Raises:
            RuntimeError: If database is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """
        Close the database connection.
        
        This method should be called during application shutdown.
        """
        if self.engine:
            logger.info("Closing database connection...")
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database connection closed")


# Global database manager instance
db_manager = DatabaseManager()


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    
    This function is used as a FastAPI dependency to inject
    database sessions into route handlers.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in db_manager.get_session():
        yield session


async def init_database() -> None:
    """
    Initialize the database.
    
    This function should be called during application startup.
    """
    await db_manager.initialize()
    await db_manager.create_tables()


async def close_database() -> None:
    """
    Close the database connection.
    
    This function should be called during application shutdown.
    """
    await db_manager.close()


async def reset_database() -> None:
    """
    Reset the database by dropping and recreating all tables.
    
    WARNING: This will delete all data. Use only for testing/development.
    """
    await db_manager.drop_tables()
    await db_manager.create_tables()
    logger.warning("Database has been reset - all data deleted")
