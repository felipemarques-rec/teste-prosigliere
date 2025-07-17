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
│   ├── security/          # Authentication & Security
│   └── web/               # Web framework (FastAPI)
│       ├── controllers/   # API route handlers
│       └── schemas/      # Pydantic schemas
└── main.py               # Application entry point
```

## 🚀 Features

- **RESTful API** with comprehensive CRUD operations
- **JWT Authentication** with secure user management
- **User Registration & Login** system
- **Password Security** with bcrypt hashing
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

### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register` | Register a new user | ❌ |
| `POST` | `/auth/login` | User login and get JWT token | ❌ |
| `GET` | `/auth/me` | Get current user information | ✅ |
| `POST` | `/auth/change-password` | Change user password | ✅ |
| `POST` | `/auth/reset-password` | Request password reset | ❌ |
| `POST` | `/auth/reset-password/confirm` | Confirm password reset | ❌ |

### Blog Posts Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/posts` | Get all blog posts with comment counts | ❌ |
| `POST` | `/api/posts` | Create a new blog post | ✅ |
| `GET` | `/api/posts/{id}` | Get specific blog post with comments | ❌ |
| `PUT` | `/api/posts/{id}` | Update a blog post | ✅ |
| `DELETE` | `/api/posts/{id}` | Delete a blog post | ✅ |

### Comments Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/posts/{id}/comments` | Add comment to blog post | ❌ |

### System Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint |
| `GET` | `/docs` | Interactive API documentation |
| `GET` | `/` | API information |

## 🛠️ Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM with async support
- **PostgreSQL** - Robust relational database
- **Pydantic** - Data validation using Python type annotations
- **JWT (python-jose)** - JSON Web Token authentication
- **bcrypt (passlib)** - Password hashing and verification
- **email-validator** - Email validation
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
# JWT_SECRET_KEY=your-secret-key-here-change-in-production
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
pip install -r requirements.txt

# Start PostgreSQL database
docker-compose up db

# Run the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔐 Authentication & Security

### JWT Token Authentication
- **Token Type**: Bearer JWT tokens
- **Expiration**: 30 minutes (configurable)
- **Algorithm**: HS256
- **Claims**: User ID, username, expiration

### Password Security
- **Hashing**: bcrypt with automatic salt generation
- **Strength Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character

### User Validation
- **Username**: 3-50 characters, alphanumeric and underscore only
- **Email**: Valid email format, unique in system
- **Password**: Complex password requirements enforced

### Protected Routes
Routes requiring authentication:
- `POST /api/posts` - Create blog post
- `PUT /api/posts/{id}` - Update blog post
- `DELETE /api/posts/{id}` - Delete blog post
- `GET /auth/me` - Get user profile
- `POST /auth/change-password` - Change password

## 🏛️ Clean Architecture Implementation

### Domain Layer
- **Entities**: `BlogPost`, `Comment`, and `User` with business rules and validation
- **Repository Interfaces**: Abstract contracts for data persistence
- **Use Cases**: Application business logic and orchestration

### Infrastructure Layer
- **Database Models**: SQLAlchemy models for data persistence
- **Repository Implementations**: Concrete database operations
- **Security Services**: Password hashing and JWT token management
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
pytest tests/test_auth.py
pytest tests/test_blog_posts.py
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

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
| `JWT_SECRET_KEY` | JWT signing secret key | `your-secret-key-here-change-in-production` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` |
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
  -e JWT_SECRET_KEY=your_production_secret_key \
  blog-api:latest
```

### Production Considerations

1. **Environment Variables**: Use secure environment variable management
2. **JWT Secret**: Use a strong, randomly generated secret key
3. **Database**: Use managed PostgreSQL service (AWS RDS, Google Cloud SQL)
4. **Reverse Proxy**: Use Nginx or similar for SSL termination
5. **Monitoring**: Implement application monitoring (Prometheus, Grafana)
6. **Logging**: Centralized logging with structured logs
7. **Rate Limiting**: Add rate limiting for API endpoints
8. **CORS**: Configure CORS for production domains

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
- Production-Ready API Development

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JWT.io](https://jwt.io/) - JWT Token Debugger
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [OAuth2 with FastAPI](https://fastapi.tiangolo.com/tutorial/security/)

**API Documentation**: Visit `/docs` endpoint for interactive Swagger documentation with authentication support.
