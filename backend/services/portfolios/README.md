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
