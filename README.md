# Portfolio Platform

[English](README.md) · [Русский](README.ru.md)

Investment tracking app: track assets, current prices, and profitability dynamics.

### Requirements

- **Docker** + **Docker Compose v2**
- **bash** (macOS/Linux; on Windows use Git Bash or WSL)
- **just** - only for development

## 🏠 Self-Hosting

Self-hosting is a single command via:

```bash
./scripts/selfhost.sh up
```

The first run automatically:

1. Generates `.env.selfhost` from `.env.selfhost.example` with a random `JWT_SECRET` (if missing)
2. Builds the backend, worker, scheduler and both frontends
3. Starts Postgres, Redis, nginx
4. Applies migrations and seeds initial data

Once running:

- User frontend: **http://localhost**
- Admin frontend: **http://localhost/admin/**
- Default admin: `admin@example.com` / `admin123`. Credentials come from `ADMIN_EMAIL` / `ADMIN_PASSWORD` in `.env.selfhost`.

### Commands

```
init            generate .env.selfhost (random JWT_SECRET)
up              build & start the stack
down            stop the stack
restart         recreate containers (applies .env.selfhost changes)
ps              list containers
status          container states + access URL
logs [svc]      show logs
logs-f [svc]    tail logs
backup          dump the database to db_backups/
backup-list     list existing backups
restore [file]  restore the DB from a backup file (default: latest)
reinit          re-run migrations and seed data (idempotent)
passwd [email]  set a new password for a user (default: ADMIN_EMAIL)
clean           stop and remove ALL data
```

### Notes

- The stack listens on host port `80`. If that port is taken, set `NGINX_PORT` in `.env.selfhost` (e.g. `NGINX_PORT=8080`) and restart.
- Worker and scheduler run by default.
- On the very first launch the market catalog and prices are populated automatically (takes a few minutes, requires internet). The scheduler will immediately execute the first tasks; then they follow the cron schedule. Manual rerun is always possible: Admin → External API → Tasks → "Run Now". If the first run failed partway (e.g. no internet), fix the problem and re-run `./scripts/selfhost.sh reinit` — it reapplies migrations and seeds without destroying data.
- Make a backup before maintenance or major changes: `./scripts/selfhost.sh backup`. Restore with `./scripts/selfhost.sh restore` (latest backup) or `./scripts/selfhost.sh restore path/to/file.sql`. Restore wipes the current database (you'll be asked to confirm).

## 🚀 Development

### Run

```bash
# Clone and start in dev mode
git clone https://github.com/bro-Nik/portfolio-platform.git
cd portfolio-platform
just up -d     # build & start in the background
```

Once started, open **http://localhost:8081** in your browser.

On first start, migrations and seed data (admin user, providers, etc.) are applied automatically.
Login: `admin@example.com` / `admin123`.

> The `.env` file is optional for development — the app works with built-in defaults.
> Copy `.env.example` to `.env` only if you need to change ports, secrets, or SMTP.

## 🛠 Development commands

```bash
just          # Show all available commands with descriptions
```

`just up` starts the worker + scheduler. To run the stack without background tasks, use
`just up-no-workers -d`.

## 📚 Structure

- [`Backend`](backend/) — FastAPI monolith (modules: auth, portfolios, market)
- [`User Frontend`](frontend/user/) — React UI
- [`Admin Frontend`](frontend/admin/) — Admin React UI
