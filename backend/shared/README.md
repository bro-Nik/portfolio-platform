# Shared Code for Backend Services

Shared modules for backend microservices.

## 📦 Modules

- [**Repositories**](./shared/repositories/) - Base CRUD repositories (async/sync)
- [**Exceptions**](./shared/exceptions/) - Common business and HTTP exceptions
- [**Rate Limit**](./shared/rate_limit/) - IP-based rate limiting

## 🚀 Quick Start

```dockerfile
COPY shared /shared
RUN pip install -e /shared
```
