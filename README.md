# Portfolio Platform

Investment portfolio management platform with microservices architecture.


## 🚀 Quick Start

```bash
# Clone and start
git clone git@github.com:bro-Nik/portfolio-platform.git
just up

# Access the application
open http://localhost
```


## 📚 Services
- [`Auth`](backend/services/auth/) - Authentication (FastAPI, PostgreSQL)
- [`Market`](backend/services/market/) - Market data (FastAPI, PostgreSQL, Celery, Redis)
- [`Portfolios`](backend/services/portfolios/) - Portfolio management (FastAPI, PostgreSQL, Redis)
- [`User Frontend`](frontend/user/) - React UI

## 🛠 Commands
```bash
just          # Show all available commands with descriptions
```
## 📜 Development History

This project is now a monorepo. The development history of individual services can be found in their archived repositories:

- Auth service history [`repo`](https://github.com/bro-Nik/portfolio-auth)
- Market service history [`repo`](https://github.com/bro-Nik/portfolio-market)
- Portfolios service history [`repo`](https://github.com/bro-Nik/portfolio-backend) (formerly `portfolio-backend`)
- User frontend history [`repo`](https://github.com/bro-Nik/portfolio-frontend)
