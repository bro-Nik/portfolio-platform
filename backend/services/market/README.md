# Market API

A microservice for managing tickers, prices and images.

## Core Features
- **Ticker Catalog**: Store and retrieve ticker metadata and images
- **Price Data**: Real-time and historical price tracking
- **Image Management**: Upload and serve ticker images
- **Background Jobs**: Celery workers fetching data from external APIs

## Tech Stack
FastAPI • PostgreSQL • Alembic • JWT • Docker • pytest • Celery • Redis

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
