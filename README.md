# Portfolio Platform

Investment portfolio management platform built with FastAPI, React, and TaskIQ.

## 🚀 Quick Start

```bash
# Clone and start
git clone git@github.com:bro-Nik/portfolio-platform.git
just up

# Access the application
open http://localhost
```

On first start, migrations and seed data (admin user, providers, etc.) are applied automatically.
Login: `admin@example.com` / `admin123`.

## 📚 Structure

- [`Backend`](backend/) — FastAPI monolith (modules: auth, portfolios, market)
- [`User Frontend`](frontend/user/) — React UI
- [`Admin Frontend`](frontend/admin/) — Admin React UI

## 🛠 Commands

```bash
just          # Show all available commands with descriptions
```

## 🏠 Self-Hosting

### Quick Start

```bash
just up-workers

```


### Requirements

- **Docker** + **Docker Compose**
- **just** (command runner)


## 📜 Development History

This project was originally a microservices architecture. The development history of individual services can be found in their archived repositories:

- Auth service history [`repo`](https://github.com/bro-Nik/portfolio-auth)
- Market service history [`repo`](https://github.com/bro-Nik/portfolio-market)
- Portfolios service history [`repo`](https://github.com/bro-Nik/portfolio-backend) (formerly `portfolio-backend`)
- User frontend history [`repo`](https://github.com/bro-Nik/portfolio-frontend)
