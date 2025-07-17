"""
Main Application Entry Point

This module contains the FastAPI application setup and configuration.
Following Clean Architecture principles, this file:
- Configures the FastAPI application
- Sets up middleware and CORS
- Registers route handlers
- Handles application lifecycle events
- Provides health check endpoints
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .infrastructure.database.database import init_database, close_database, db_manager
from .infrastructure.web.controllers.blog_post_controller import router as blog_post_router
from .infrastructure.web.controllers.comment_controller import router as comment_router
from .infrastructure.web.controllers.auth_controller import router as auth_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    message: str
    database: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting Blog API application...")
    
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    logger.info("Blog API application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Blog API application...")
    
    try:
        await close_database()
        logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")
    
    logger.info("Blog API application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Blog API",
    description="""
    A RESTful API for managing a simple blogging platform.

    Architecture
    
    This API follows Clean Architecture principles with:
    - Domain Layer: Business entities and rules
    - Application Layer: Use cases and business logic
    - Infrastructure Layer: Database, web framework, and external concerns
    """,
    version="1.0.0",
    contact={
        "name": "Blog API Support",
        "email": "support@blogapi.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Check the health status of the API and its dependencies"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of the API and its dependencies,
    including database connectivity.
    """
    try:
        # Check database health
        db_healthy = await db_manager.health_check()
        
        if db_healthy:
            return HealthResponse(
                status="healthy",
                message="API is running normally",
                database="connected"
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "message": "Database connection failed",
                    "database": "disconnected"
                }
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "database": "unknown"
            }
        )


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Welcome message and API information"
)
async def root():
    """
    API root endpoint.
    
    Returns welcome message and basic API information.
    """
    return {
        "message": "Welcome to the Blog API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "posts": "/api/posts",
            "create_post": "POST /api/posts",
            "get_post": "GET /api/posts/{id}",
            "add_comment": "POST /api/posts/{id}/comments"
        }
    }


# Register routers
app.include_router(blog_post_router)
app.include_router(comment_router)
app.include_router(auth_router)


# Additional metadata for OpenAPI
app.openapi_tags = [
    {
        "name": "Authentication",
        "description": "User authentication and authorization operations. Register, login, and manage user accounts.",
    },
    {
        "name": "Blog Posts",
        "description": "Operations with blog posts. Create, read, update, and delete blog posts.",
    },
    {
        "name": "Comments",
        "description": "Operations with comments. Add comments to blog posts.",
    },
    {
        "name": "Health",
        "description": "Health check endpoints for monitoring.",
    },
    {
        "name": "Root",
        "description": "Root endpoint with API information.",
    },
]


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
