# Portfolio Platform

Investment portfolio management platform with microservices architecture.

## 🏗 Architecture

```
portfolio-platform/ # This repository (orchestration)
├── auth/
├── frontend/
└── backend/
```
 
## 🚀 Quick Start

```bash
# Clone with submodules
git clone --recurse-submodules git@github.com:bro-Nik/portfolio-platform.git
cd portfolio-platform

# Start all services
docker-compose up -d

# Access the application
open http://localhost
```

## 📚 Services

- Auth: FastAPI for auth management [(repository)](https://github.com/bro-Nik/portfolio-auth).
- Frontend: React application [(repository)](https://github.com/bro-Nik/portfolio-frontend).
- Backend: FastAPI for user operations [(repository)](https://github.com/bro-Nik/portfolio-backend).

## 🛠 Tech Stack

- Auth: FastAPI, PostgreSQL
- Frontend: React
- Backend: FastAPI, PostgreSQL, Redis
- Infra: Docker, Nginx, GitHub Actions
