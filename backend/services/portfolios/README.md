# Portfolios API

A microservice for managing user portfolios and wallets.

## Core Features
- **Portfolio & wallet management**: CRUD operations
- **Asset tracking**: Monitor assets in portfolios and wallets
- **Transaction processing**: Buy, Sell, Transfer operations
- **Allocation analysis**: View asset distribution

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
