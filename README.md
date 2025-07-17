# Blog API - RESTful Blogging Platform

A production-ready RESTful API for managing a simple blogging platform built with **FastAPI**, following **Clean Architecture** principles and **SOLID** design patterns.

## 🏗️ Architecture Overview

This project implements **Clean Architecture** with clear separation of concerns:

```
src/
├── domain/                    # Enterprise Business Rules
│   ├── entities/             # Domain entities with business logic
│   ├── repositories/         # Repository interfaces (abstractions)
│   └── use_cases/           # Application business rules
├── infrastructure/          # Frameworks & Drivers
│   ├── database/           # Database implementation
│   │   ├── models/         # SQLAlchemy models
│   │   └── repositories/   # Repository implementations
│   └── web/               # Web framework (FastAPI)
│       ├── controllers/   # API route handlers
│       └── schemas/      # Pydantic schemas
└── main.py               # Application entry point
```

## 🚀 Features

- **RESTful API** with comprehensive CRUD operations
- **Clean Architecture** with dependency inversion
- **SOLID Principles** implementation
- **Async/Await** support with SQLAlchemy
- **PostgreSQL** database with connection pooling
- **Pydantic** validation and serialization
- **FastAPI** with automatic OpenAPI documentation
- **Docker** containerization
- **Production-ready** error handling and logging
- **Health check** endpoints
- **Comprehensive documentation**

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/posts` | Get all blog posts with comment counts |
| `POST` | `/api/posts` | Create a new blog post |
| `GET` | `/api/posts/{id}` | Get specific blog post with comments |
| `POST` | `/api/posts/{id}/comments` | Add comment to blog post |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/docs` | Interactive API documentation |

## 🛠️ Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM with async support
- **PostgreSQL** - Robust relational database
- **Pydantic** - Data validation using Python type annotations
- **Alembic** - Database migration tool
- **Docker** - Containerization platform
- **pytest** - Testing framework

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if running locally)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd blog-api
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# DATABASE_URL=postgresql+asyncpg://blog_user:blog_password@localhost:5432/blog_db
```

### 3. Using Docker (Recommended)

```bash
# Start the application with Docker Compose
docker-compose up --build

# The API will be available at http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### 4. Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Start PostgreSQL database
docker-compose up db

# Run the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 API Usage Examples

### Create a Blog Post

```bash
curl -X POST "http://localhost:8000/api/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post..."
  }'
```

### Get All Blog Posts

```bash
curl -X GET "http://localhost:8000/api/posts"
```

### Get Specific Blog Post with Comments

```bash
curl -X GET "http://localhost:8000/api/posts/{post_id}"
```

### Add Comment to Blog Post

```bash
curl -X POST "http://localhost:8000/api/posts/{post_id}/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great blog post!",
    "author_name": "John Doe",
    "author_email": "john@example.com"
  }'
```

## 🏛️ Clean Architecture Implementation

### Domain Layer
- **Entities**: `BlogPost` and `Comment` with business rules and validation
- **Repository Interfaces**: Abstract contracts for data persistence
- **Use Cases**: Application business logic and orchestration

### Infrastructure Layer
- **Database Models**: SQLAlchemy models for data persistence
- **Repository Implementations**: Concrete database operations
- **Web Controllers**: FastAPI route handlers
- **Schemas**: Pydantic models for API validation

### Key Design Patterns
- **Repository Pattern**: Abstraction over data access
- **Dependency Injection**: Loose coupling between layers
- **Factory Pattern**: Object creation and configuration
- **Strategy Pattern**: Interchangeable algorithms and implementations

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_blog_posts.py
```

## 📊 Database Schema

### Blog Posts Table
```sql
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Comments Table
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    author_name VARCHAR(100) DEFAULT 'Anonymous',
    author_email VARCHAR(255) DEFAULT '',
    is_approved BOOLEAN DEFAULT TRUE,
    blog_post_id UUID REFERENCES blog_posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://blog_user:blog_password@localhost:5432/blog_db` |
| `DATABASE_POOL_SIZE` | Connection pool size | `10` |
| `DATABASE_MAX_OVERFLOW` | Max overflow connections | `20` |
| `DEBUG` | Enable debug mode | `True` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## 📈 Monitoring and Health Checks

### Health Check Endpoint
```bash
curl -X GET "http://localhost:8000/health"
```

Response:
```json
{
  "status": "healthy",
  "message": "API is running normally",
  "database": "connected"
}
```

## 🚀 Production Deployment

### Docker Production Build

```bash
# Build production image
docker build -t blog-api:latest .

# Run production container
docker run -d \
  --name blog-api \
  -p 8000:8000 \
  -e DATABASE_URL=your_production_db_url \
  blog-api:latest
```

### Production Considerations

1. **Environment Variables**: Use secure environment variable management
2. **Database**: Use managed PostgreSQL service (AWS RDS, Google Cloud SQL)
3. **Reverse Proxy**: Use Nginx or similar for SSL termination
4. **Monitoring**: Implement application monitoring (Prometheus, Grafana)
5. **Logging**: Centralized logging with structured logs
6. **Security**: Implement authentication and authorization
7. **Rate Limiting**: Add rate limiting for API endpoints

## 🔮 Next Steps (Future Enhancements)

If I had more time, I would implement:

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- User management system

### Advanced Features
- **Search & Filtering**: Full-text search for blog posts
- **Pagination**: Cursor-based pagination for better performance
- **Caching**: Redis caching for frequently accessed data
- **File Uploads**: Support for images and attachments
- **Email Notifications**: Comment notifications to post authors

### API Enhancements
- **Versioning**: API versioning strategy
- **Rate Limiting**: Request throttling and quotas
- **Webhooks**: Event-driven notifications
- **GraphQL**: Alternative query interface

### DevOps & Monitoring
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Application performance monitoring (APM)
- **Metrics**: Custom business metrics and dashboards
- **Alerting**: Automated error detection and notifications

### Testing & Quality
- **Integration Tests**: End-to-end API testing
- **Load Testing**: Performance and scalability testing
- **Security Testing**: Vulnerability scanning
- **Code Quality**: Static analysis and linting automation

### Database Optimizations
- **Indexing**: Query optimization and performance tuning
- **Migrations**: Automated database schema management
- **Backup Strategy**: Automated backups and disaster recovery
- **Read Replicas**: Database scaling for read operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Felipe Marques da Silva**
- Clean Architecture & SOLID Principles Expert
- FastAPI & SQLAlchemy Specialist
- Production-Ready API Development

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

**API Documentation**: Visit `/docs` endpoint for interactive Swagger documentation.
