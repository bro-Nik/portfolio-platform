# -------------------- Variables --------------------

compose := "-f compose.base.yml -f compose.dev.yml"
backend_path := "backend"
backup_dir := "./db_backups"

set dotenv-load := true
set unstable := true

db_name := env_var_or_default("POSTGRES_DB", "portfolios")
db_user := env_var_or_default("POSTGRES_USER", "portfolios")

# -------------------- Core commands --------------------
default:
    @echo 'Available commands:'
    @echo ''
    @echo 'Run and stop:'
    @echo '  just up [args]             - Start the project with workers (e.g.: just up -d)'
    @echo '  just up-no-workers [args]  - Start the project without workers'
    @echo '  just down                  - Stop the project'
    @echo '  just restart               - Restart the project'
    @echo '  just ps                    - List containers'
    @echo ''
    @echo 'Logs and debugging:'
    @echo '  just logs [service]        - Show logs (e.g.: just logs, just logs backend)'
    @echo '  just logs-f [service]      - Follow logs'
    @echo '  just shell service         - Enter a container (backend, db, redis, nginx)'
    @echo '  just exec service [cmd]    - Run a command in a container'
    @echo ''
    @echo 'Backend development:'
    @echo '  just tests [args]          - Run tests'
    @echo '  just build-local-env       - Create a local env for LSP support'
    @echo ''
    @echo 'Databases:'
    @echo '  just backup                - Back up the database'
    @echo '  just restore-latest        - Restore from the latest backup'
    @echo '  just restore-file file     - Restore from a file'
    @echo '  just backup-list           - List backups'
    @echo '  just backup-del [keep=5]   - Delete old backups'
    @echo ''
    @echo 'Migrations:'
    @echo '  just migrate               - Apply migrations'
    @echo '  just migrate-new msg       - Create a migration'
    @echo '  just migrate-down          - Roll back the last migration'
    @echo '  just migrate-current       - Show the current migration'
    @echo ''
    @echo 'Cleanup:'
    @echo '  just clean                 - Stop and remove all data'

# -------------------- Run and stop --------------------
up *args:
    @docker compose {{ compose }} --profile worker up {{ args }}

up-no-workers *args:
    @docker compose {{ compose }} up {{ args }}

down:
    @docker compose {{ compose }} down

restart:
    @docker compose {{ compose }} restart

ps:
    @docker compose {{ compose }} ps

# -------------------- Logs --------------------
logs service="":
    @docker compose {{ compose }} logs {{ service }}

logs-f service="":
    @docker compose {{ compose }} logs -f {{ service }}

# -------------------- Container access --------------------
shell service:
    @just _ensure_app {{ service }}
    @docker compose {{ compose }} exec {{ service }} sh

exec service cmd:
    @just _ensure_app {{ service }}
    @docker compose {{ compose }} exec {{ service }} {{ cmd }}

# -------------------- Backend development --------------------

# Run the tests
tests *args:
    @docker compose -f compose.test.yml run --rm backend-tests {{ args }}; status=$$?; \
    docker compose -f compose.test.yml down --remove-orphans > /dev/null 2>&1; \
    exit $$status

# Create a local environment for LSP autocompletion
build-local-env:
    @echo "🔧 Setting up a local environment for LSP..."
    @python3 -m venv {{ backend_path }}/.venv
    @{{ backend_path }}/.venv/bin/pip install --upgrade pip
    @{{ backend_path }}/.venv/bin/pip install -r {{ backend_path }}/requirements.txt -r {{ backend_path }}/requirements-test.txt

# -------------------- Databases --------------------

# Create a backup
backup:
    @just _ensure_app db
    @echo "💾 Creating a backup..."; \
    timestamp=$(date +%Y%m%d_%H%M%S); \
    filename="{{ backup_dir }}/$timestamp.sql"; \
    mkdir -p {{ backup_dir }}; \
    if docker compose {{ compose }} exec -T db pg_dump -U {{ db_user }} {{ db_name }} > $filename; then \
    	echo "  ✅ Saved: $filename"; \
    else \
    	echo "  ❌ Backup failed"; rm -f "$filename"; exit 1; fi

# Restore from the latest backup
restore-latest:
    @latest=$(ls -t {{ backup_dir }}/*.sql 2>/dev/null | head -1); \
    [ -n "$latest" ] || { echo "❌ No backups"; exit 1; }; \
    just _ensure_app db; \
    echo "💾 Restoring from $latest..."; \
    if cat "$latest" | docker compose {{ compose }} exec -T db psql -U {{ db_user }} -d {{ db_name }}; then \
    	echo "  ✅ Restored"; \
    else \
    	echo "  ❌ Restore failed"; exit 1; fi

# Restore from a specific file
restore-file file:
    @[ -f "{{ file }}" ] || { echo "❌ File not found"; exit 1; }; \
    just _ensure_app db; \
    echo "💾 Restoring from {{ file }}..."; \
    if cat "{{ file }}" | docker compose {{ compose }} exec -T db psql -U {{ db_user }} -d {{ db_name }}; then \
    	echo "  ✅ Restored"; \
    else \
    	echo "  ❌ Restore failed"; exit 1; fi

# List backups
backup-list:
    @[ "$(just _has_backups)" = "true" ] || { echo "❌ No backups"; exit 0; }; \
    echo "💾 Backups:"; \
    ls -1 {{ backup_dir }}/*.sql | sed 's/^/  📄 /'; \
    total_size=$(du -sh {{ backup_dir }} | cut -f1); \
    echo "  📊 Total size: $total_size"

# Delete old backups
backup-del keep="5":
    @echo "🧹 Cleaning up backups..."; \
    total=$(ls -1 {{ backup_dir }}/*.sql 2>/dev/null | wc -l); \
    if [ "{{ keep }}" = "0" ]; then \
    	rm -v {{ backup_dir }}/*.sql 2>/dev/null | sed 's/^/  /'; \
    	echo "  ✅ All backups deleted"; \
    elif [ $total -le {{ keep }} ]; then \
    	echo "  ✅ Only $total backups (<= {{ keep }}), nothing to delete"; \
    else \
    	ls -t {{ backup_dir }}/*.sql | tail -n $((total - {{ keep }})) | xargs rm -v | sed 's/^/  /'; \
    	echo "  ✅ Keeping {{ keep }} backups"; \
    fi

# -------------------- Migrations --------------------

# Apply migrations
migrate:
    @started=$(just _ensure_db); \
    docker compose {{ compose }} run --rm backend alembic upgrade head; status=$?; \
    [ "$started" = "true" ] && just _stop_db; \
    exit $status

# Create a new migration
migrate-new msg:
    @docker compose {{ compose }} run --rm backend alembic revision --autogenerate -m "{{ msg }}"

# Roll back the latest migration
migrate-down:
    @started=$(just _ensure_db); \
    docker compose {{ compose }} run --rm backend alembic downgrade -1; status=$?; \
    [ "$started" = "true" ] && just _stop_db; \
    exit $status

# Show the current migration
migrate-current:
    @started=$(just _ensure_db); \
    docker compose {{ compose }} run --rm backend alembic current; status=$?; \
    [ "$started" = "true" ] && just _stop_db; \
    exit $status

# -------------------- Cleanup --------------------
clean:
    @read -p "❗ This will delete ALL data! Continue? (y/N) " confirm; \
    [ "$confirm" = "y" ] && docker compose {{ compose }} down -v && echo "✅" || echo "❌"

# -------------------- Private recipes --------------------
_has_backups:
    @[ -d "{{ backup_dir }}" ] && ls {{ backup_dir }}/*.sql 2>/dev/null | head -1 | grep -q . && echo "true" || echo "false"

_ensure_app service:
    @if ! docker compose {{ compose }} ps --status running | grep -q {{ service }}; then \
    	docker compose {{ compose }} up -d {{ service }} > /dev/null 2>&1; \
    	sleep 3; echo "true"; \
    else \
    	echo "false"; fi

_ensure_db:
    @if ! docker compose {{ compose }} ps --status running | grep -q db; then \
    	docker compose {{ compose }} up -d db > /dev/null 2>&1; \
    	sleep 5; echo "true"; \
    else \
    	echo "false"; fi

_stop_db:
    @docker compose {{ compose }} stop db > /dev/null 2>&1