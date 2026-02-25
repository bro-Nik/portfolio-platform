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
just              # Show all available commands
just up *args     # Start service in Docker (http://localhost:8000)
just down         # Stop service
just logs         # View logs
just shell        # Open shell in container
just clean        # Remove containers and volumes
just tests *args  # Run all tests
```

## API Docs (when running)
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration
See environment variables in `.env.example`
