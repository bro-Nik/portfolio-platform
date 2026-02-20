# Auth API

A microservice for authentication and user management.

## Core Features
- **Authentication**: Registration, login, logout, token refresh
- **Security**: JWT tokens (access/refresh), password hashing
- **User Management**: CRUD operations, role-based model (USER, MODERATOR, ADMIN)
- **Monitoring**: Session tracking, user activity, login logging

## Tech Stack
FastAPI • PostgreSQL • Alembic • JWT • Docker • pytest

## Quick Start

### Development
```bash
just up        # Start service in Docker (http://localhost:8000)
just logs      # View logs
just down      # Stop service
just shell     # Open shell in container
just clean     # Remove containers and volumes
```

### Testing
```bash
just test      # Run all tests
just test b    # Rebuild and run tests
```

### Migrations
```bash
just migrate           # Apply pending migrations
just migrate-new "msg" # Create new migration
just migrate-down      # Rollback last migration
just migrate-current   # Check migration status
```

## API Docs (when running)
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration
See environment variables in `.env.example`
