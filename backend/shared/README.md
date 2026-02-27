# Shared Code for Backend Services

Shared modules for backend microservices.

## 📦 Modules

- [**Repositories**](./shared/repositories/) - Base CRUD repositories (async/sync)
- [**Exceptions**](./shared/exceptions/) - Common business and HTTP exceptions
- [**Rate Limit**](./shared/rate_limit/) - IP-based rate limiting
- [**API**](./shared/api/) - API utilities
- [**Dependencies**](./shared/dependencies/) - FastAPI dependencies
- [**Schemas**](./shared/schemas/) - Shared Pydantic models
- [**Utils**](./shared/utils/) - Utility functions

## 🚀 Quick Start

```dockerfile
COPY shared /shared
RUN pip install -e /shared
```
