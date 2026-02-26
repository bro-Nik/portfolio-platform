# Shared Code for Backend Services

Shared modules for backend microservices.

## 📦 Modules

- [**Repositories**](./shared/repositories/README.md) - Base CRUD repositories (async/sync)
- [**Exceptions**](./shared/exceptions/README.md) - Common business and HTTP exceptions

## 🚀 Quick Start

```dockerfile
COPY shared /shared
RUN pip install -e /shared
```
