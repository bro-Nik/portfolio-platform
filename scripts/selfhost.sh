#!/usr/bin/env bash
#
# Portfolios Platform — self-hosting runner.
#
# Works on macOS / Linux (and Windows via Git Bash or WSL).
# Requires: Docker + Docker Compose v2.
#
# Usage:
#   ./scripts/selfhost.sh init          Generate .env.selfhost from the template
#                                       with a random JWT_SECRET
#   ./scripts/selfhost.sh up            Build and start the stack (auto-inits .env.selfhost)
#   ./scripts/selfhost.sh down          Stop the stack
#   ./scripts/selfhost.sh restart       Recreate & restart (picks up .env.selfhost changes)
#   ./scripts/selfhost.sh ps            List containers
#   ./scripts/selfhost.sh status        Show container state and access URL
#   ./scripts/selfhost.sh logs [svc]    Show logs (optionally of one service)
#   ./scripts/selfhost.sh logs-f [svc]  Tail logs
#   ./scripts/selfhost.sh backup        Dump the database to db_backups/
#   ./scripts/selfhost.sh backup-list   List existing backups
#   ./scripts/selfhost.sh restore [f]   Restore from a backup file (default: latest),
#                                        wipes the current database (asks for confirmation)
#   ./scripts/selfhost.sh reinit        Re-run migrations and seed (idempotent)
#   ./scripts/selfhost.sh passwd [email] Set a new password for a user
#                                        (default: ADMIN_EMAIL), no mail needed
#   ./scripts/selfhost.sh clean         Stop and delete ALL data (dangerous)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILE="${COMPOSE_FILE:-compose.selfhost.yml}"
ENV_FILE="${ENV_FILE:-.env.selfhost}"
ENV_TEMPLATE="${ENV_TEMPLATE:-.env.selfhost.example}"
BACKUP_DIR="${BACKUP_DIR:-./db_backups}"
COMPOSE=(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE")

# Reads a value from the env file (with fallback). Used for Postgres user/db,
# which can be overridden via POSTGRES_USER / POSTGRES_DB.
env_value() {  # env_value KEY fallback
  local v
  v="$(grep "^$1=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '[:space:]' || true)"
  echo "${v:-$2}"
}

log() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m==>\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m==>\033[0m %s\n' "$*" >&2; }

# Returns the host URL suffix for NGINX_PORT, e.g. ":8080" (empty when port 80).
nginx_url_part() {
  local port
  port="$(grep '^NGINX_PORT=' "$ENV_FILE" | cut -d= -f2- | tr -d '[:space:]' || true)"
  port="${port:-80}"
  [ "$port" = "80" ] || printf ':%s' "$port"
}

ensure_env_file() {
  log "Using env file: $ENV_FILE"
  if [ ! -f "$ENV_FILE" ]; then
    warn "$ENV_FILE not found, running 'init' first..."
    cmd_init
  fi
}

cmd_init() {
  if [ -f "$ENV_FILE" ]; then
    warn "$ENV_FILE already exists — leaving it untouched."
    return
  fi

  log "Creating $ENV_FILE from $ENV_TEMPLATE..."

  if [ ! -f "$ENV_TEMPLATE" ]; then
    err "Template $ENV_TEMPLATE not found. Aborting."
    exit 1
  fi

  cp "$ENV_TEMPLATE" "$ENV_FILE"

  jwt_secret="$(openssl rand -hex 48 2>/dev/null || true)"
  jwt_secret="${jwt_secret:-change-me-to-a-unique-long-random-secret}"

  # The template is already production-oriented; only the auth secret is replaced.
  _sed "s|^JWT_SECRET=.*|JWT_SECRET=${jwt_secret}|" "$ENV_FILE"

  log "$ENV_FILE created with a random JWT_SECRET."
  log "It is ignored by git — keep it safe and don't commit it."
  log "Set NGINX_PORT if port 80 is busy."
  log "Change the default admin password: ./scripts/selfhost.sh passwd"
}

# Portable in-place sed (works on BSD/macOS and GNU/Linux).
_sed() {
  local expr="$1" file="$2"
  sed -i.bak.$$ "$expr" "$file"
  rm -f "$file.bak.$$"
}

cmd_up() {
  ensure_env_file
  log "Building and starting the stack ($COMPOSE_FILE)..."
  "${COMPOSE[@]}" up -d --build
  log "Done."

  url_part="$(nginx_url_part)"

  printf '\n'
  printf '  User frontend :  http://localhost%s\n' "$url_part"
  printf '  Admin frontend:  http://localhost%s/admin\n' "$url_part"
  printf '  Default admin :  %s / %s (see %s)\n' \
    "$(grep '^ADMIN_EMAIL=' "$ENV_FILE" | cut -d= -f2-)" \
    "$(grep '^ADMIN_PASSWORD=' "$ENV_FILE" | cut -d= -f2-)" \
    "$ENV_FILE"
}

cmd_down() {
  ensure_env_file
  log "Stopping the stack..."
  "${COMPOSE[@]}" down
}

cmd_restart() {
  ensure_env_file
  log "Recreating the stack so .env.selfhost changes take effect..."
  "${COMPOSE[@]}" up -d --force-recreate
}

cmd_ps() {
  ensure_env_file
  "${COMPOSE[@]}" ps
}

cmd_status() {
  ensure_env_file
  "${COMPOSE[@]}" ps
  printf '\n  http://localhost%s\n' "$(nginx_url_part)"
}

cmd_logs() {
  ensure_env_file
  "${COMPOSE[@]}" logs --tail=200 ${1:+$1}
}

cmd_logs_f() {
  ensure_env_file
  "${COMPOSE[@]}" logs -f ${1:+$1}
}

cmd_backup() {
  ensure_env_file
  mkdir -p "$BACKUP_DIR"
  local file="$BACKUP_DIR/$(date +%Y%m%d_%H%M%S).sql"
  local db_user="$(env_value POSTGRES_USER postgres)"
  local db_name="$(env_value POSTGRES_DB postgres)"
  log "Creating backup → $file"
  "${COMPOSE[@]}" exec -T db pg_dump -U "$db_user" "$db_name" >"$file"
  log "Backup saved: $file"
}

cmd_backup_list() {
  if [ -d "$BACKUP_DIR" ]; then
    ls -1 "$BACKUP_DIR"/*.sql 2>/dev/null | sed 's#^#  #' \
      || warn "No backups yet."
  else
    warn "No backups yet."
  fi
}

cmd_restore() {
  ensure_env_file
  local file="${1:-}"
  if [ -z "$file" ]; then
    file="$(ls -t "$BACKUP_DIR"/*.sql 2>/dev/null | head -1 || true)"
    [ -n "$file" ] || { err "No backup files in $BACKUP_DIR and no file given."; exit 1; }
    log "No file given, using latest backup."
  fi
  [ -f "$file" ] || { err "Backup file not found: $file"; exit 1; }

  local db_user="$(env_value POSTGRES_USER postgres)"
  local db_name="$(env_value POSTGRES_DB postgres)"

  log "This will WIPE the current database and replace it with: $file"
  read -rp "Proceed? (y/N) " confirm
  case "$confirm" in
    y | Y | yes | YES) ;;
    *) err "Aborted."; exit 1 ;;
  esac

  log "Stopping app containers before restore..."
  "${COMPOSE[@]}" stop backend worker scheduler init > /dev/null 2>&1 || true

  log "Dropping and recreating the public schema..."
  if ! "${COMPOSE[@]}" exec -T db psql -U "$db_user" "$db_name" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" > /dev/null; then
    err "Failed to clean the database. Restore aborted."
    "${COMPOSE[@]}" up -d
    exit 1
  fi

  log "Restoring from $file..."
  if "${COMPOSE[@]}" exec -T db psql -U "$db_user" "$db_name" < "$file"; then
    log "Restore done. Restarting the stack..."
    "${COMPOSE[@]}" up -d
  else
    err "Restore failed."
    log "Restarting the stack..."
    "${COMPOSE[@]}" up -d
    exit 1
  fi
}

cmd_reinit() {
  ensure_env_file
  log "Re-running migrations and seed data..."
  "${COMPOSE[@]}" run --rm init
  log "Done. (seed is idempotent: it only creates the admin if no users exist)"
}

# Ensures the backend is running so account management commands can exec into it.
ensure_backend() {
  if ! "${COMPOSE[@]}" ps --status running 2>/dev/null | grep -q backend; then
    log "backend is not running — starting db and backend..."
    "${COMPOSE[@]}" up -d db backend > /dev/null
    for _ in $(seq 1 30); do
      "${COMPOSE[@]}" ps --status running 2>/dev/null | grep -q backend && return
      sleep 2
    done
    err "backend did not start in time. Check the logs: $0 logs backend"
    exit 1
  fi
}

cmd_passwd() {
  ensure_env_file
  local email="${1:-$(env_value ADMIN_EMAIL admin@example.com)}"
  read -rsp "New password for $email: " pw1
  printf '\n'
  read -rsp "Confirm password: " pw2
  printf '\n'
  [ -n "$pw1" ] || { err "Password cannot be empty."; exit 1; }
  [ "$pw1" = "$pw2" ] || { err "Passwords do not match."; exit 1; }
  ensure_backend
  printf '%s\n' "$pw1" | "${COMPOSE[@]}" exec -T backend python -m app.scripts.account --email "$email"
  log "Password updated for $email."
}

cmd_clean() {
  ensure_env_file
  log "This will STOP the stack and DELETE ALL DATA (postgres/redis volumes)."
  read -rp "Proceed? (y/N) " confirm
  case "$confirm" in
    y | Y | yes | YES)
      "${COMPOSE[@]}" down -v
      log "Done."
      ;;
    *)
      err "Aborted."
      ;;
  esac
}

help_text() {
  echo "Usage: $0 <command>"
  echo
  echo "  init           generate .env.selfhost (random JWT_SECRET)"
  echo "  up             build & start the stack"
  echo "  down           stop the stack"
  echo "  restart        recreate containers (applies .env.selfhost changes)"
  echo "  ps             list containers"
  echo "  status         containers + URL"
  echo "  logs [svc]     show logs"
  echo "  logs-f [svc]   tail logs"
  echo "  backup         dump database to db_backups/"
  echo "  backup-list    list backups"
  echo "  restore [file] restore DB from a backup file (default: latest, wipes current data)"
  echo "  reinit         re-run migrations and seed data"
  echo "  passwd [email] set a new password for a user (default: ADMIN_EMAIL)"
  echo "  clean          stop and remove all data"
}

case "${1:-}" in
  init) cmd_init ;;
  up) cmd_up ;;
  down) cmd_down ;;
  restart) cmd_restart ;;
  ps) cmd_ps ;;
  status) cmd_status ;;
  logs) shift; cmd_logs "${1:-}" ;;
  logs-f) shift; cmd_logs_f "${1:-}" ;;
  backup) cmd_backup ;;
  backup-list) cmd_backup_list ;;
  restore) shift; cmd_restore "${1:-}" ;;
  reinit) cmd_reinit ;;
  passwd) shift; cmd_passwd "${1:-}" ;;
  clean) cmd_clean ;;
  "" | -h | --help | help) help_text ;;
  *) err "Unknown command: $1"; help_text; exit 1 ;;
esac
