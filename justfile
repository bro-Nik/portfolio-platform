# -------------------- Переменные --------------------

compose := "-f compose.base.yml -f compose.dev.yml"
backend_path := "backend"
backup_dir := "./db_backups"

set dotenv-load := true
set unstable := true

db_name := env_var_or_default("POSTGRES_DB", "portfolios")
db_user := env_var_or_default("POSTGRES_USER", "portfolios")

# -------------------- Основные команды --------------------
default:
    @echo 'Доступные команды:'
    @echo ''
    @echo 'Запуск и остановка:'
    @echo '  just up [args]             - Запустить проект (пример: just up -d)'
    @echo '  just up-workers [args]     - Запустить проект с воркерами taskiq'
    @echo '  just down                  - Остановить проект'
    @echo '  just restart               - Перезапустить проект'
    @echo '  just ps                    - Список контейнеров'
    @echo ''
    @echo 'Логи и отладка:'
    @echo '  just logs [service]        - Показать логи (пример: just logs, just logs backend)'
    @echo '  just logs-f [service]      - Следить за логами'
    @echo '  just shell service         - Войти в контейнер (backend, db, redis, nginx)'
    @echo '  just exec service [cmd]    - Выполнить команду'
    @echo ''
    @echo 'Разработка Backend:'
    @echo '  just tests [args]          - Запустить тесты'
    @echo '  just build-local-env       - Создать локальное окружение для LSP'
    @echo ''
    @echo 'Базы данных:'
    @echo '  just backup                - Сделать бэкап БД'
    @echo '  just restore-latest        - Восстановить БД из последнего бэкапа'
    @echo '  just restore-file file     - Восстановить из файла'
    @echo '  just backup-list           - Список бэкапов'
    @echo '  just backup-del [keep=5]   - Удалить старые бэкапы'
    @echo ''
    @echo 'Миграции:'
    @echo '  just migrate                    - Применить миграции'
    @echo '  just migrate-new msg            - Создать миграцию'
    @echo '  just migrate-down               - Откатить последнюю миграцию'
    @echo '  just migrate-current            - Показать текущую миграцию'
    @echo ''
    @echo 'Очистка:'
    @echo '  just clean                 - Остановить и удалить данные'

# -------------------- Запуск и остановка --------------------
up *args:
    @docker compose {{ compose }} up {{ args }}

up-workers *args:
    @docker compose {{ compose }} --profile worker up {{ args }}

down:
    @docker compose {{ compose }} down

restart:
    @docker compose {{ compose }} restart

ps:
    @docker compose {{ compose }} ps

# -------------------- Логи --------------------
logs service="":
    @docker compose {{ compose }} logs {{ service }}

logs-f service="":
    @docker compose {{ compose }} logs -f {{ service }}

# -------------------- Доступ к контейнерам --------------------
shell service:
    @just _ensure_app {{ service }}
    @docker compose {{ compose }} exec {{ service }} sh

exec service cmd:
    @just _ensure_app {{ service }}
    @docker compose {{ compose }} exec {{ service }} {{ cmd }}

# -------------------- Разработка Backend --------------------

# Запустить тесты
tests *args:
    @docker compose -f compose.test.yml run --rm backend-tests {{ args }}

# Создать локальное окружение для автодополнения (LSP)
build-local-env:
    @echo "🔧 Настройка локального окружения для LSP..."
    @python3 -m venv {{ backend_path }}/.venv
    @{{ backend_path }}/.venv/bin/pip install --upgrade pip
    @{{ backend_path }}/.venv/bin/pip install -r {{ backend_path }}/requirements.txt -r {{ backend_path }}/requirements-test.txt

# -------------------- Базы данных --------------------

# Создать бэкап
backup:
    @just _ensure_app db
    @echo "💾 Создание бэкапа..."; \
    timestamp=$(date +%Y%m%d_%H%M%S); \
    filename="{{ backup_dir }}/$timestamp.sql"; \
    mkdir -p {{ backup_dir }}; \
    if docker compose {{ compose }} exec -T db pg_dump -U {{ db_user }} {{ db_name }} > $filename; then \
    	echo "  ✅ Сохранено: $filename"; \
    else \
    	echo "  ❌ Ошибка создания бэкапа"; rm -f "$filename"; exit 1; fi

# Восстановить из последнего бэкапа
restore-latest:
    @latest=$(ls -t {{ backup_dir }}/*.sql 2>/dev/null | head -1); \
    [ -n "$latest" ] || { echo "❌ Нет бэкапов"; exit 1; }; \
    just _ensure_app db; \
    echo "💾 Восстановление из $latest..."; \
    if cat "$latest" | docker compose {{ compose }} exec -T db psql -U {{ db_user }} -d {{ db_name }}; then \
    	echo "  ✅ Восстановлено"; \
    else \
    	echo "  ❌ Ошибка восстановления"; exit 1; fi

# Восстановить из конкретного файла
restore-file file:
    @[ -f "{{ file }}" ] || { echo "❌ Файл не найден"; exit 1; }; \
    just _ensure_app db; \
    echo "💾 Восстановление из {{ file }}..."; \
    if cat "{{ file }}" | docker compose {{ compose }} exec -T db psql -U {{ db_user }} -d {{ db_name }}; then \
    	echo "  ✅ Восстановлено"; \
    else \
    	echo "  ❌ Ошибка восстановления"; exit 1; fi

# Список бэкапов
backup-list:
    @[ "$(just _has_backups)" = "true" ] || { echo "❌ Нет бэкапов"; exit 0; }; \
    echo "💾 Бэкапы:"; \
    ls -1 {{ backup_dir }}/*.sql | sed 's/^/  📄 /'; \
    total_size=$(du -sh {{ backup_dir }} | cut -f1); \
    echo "  📊 Общий размер: $total_size"

# Удалить бэкапы
backup-del keep="5":
    @echo "🧹 Очистка бэкапов..."; \
    total=$(ls -1 {{ backup_dir }}/*.sql 2>/dev/null | wc -l); \
    if [ "{{ keep }}" = "0" ]; then \
    	rm -v {{ backup_dir }}/*.sql 2>/dev/null | sed 's/^/  /'; \
    	echo "  ✅ Все бэкапы удалены"; \
    elif [ $total -le {{ keep }} ]; then \
    	echo "  ✅ Всего $total бэкапов (<= {{ keep }}), ничего не удалено"; \
    else \
    	ls -t {{ backup_dir }}/*.sql | tail -n $((total - {{ keep }})) | xargs rm -v | sed 's/^/  /'; \
    	echo "  ✅ Оставлено {{ keep }} бэкапов"; \
    fi

# -------------------- Миграции --------------------

# Применить миграции
migrate:
    @started=$(just _ensure_db); \
    docker compose {{ compose }} run --rm backend alembic upgrade head; status=$?; \
    [ "$started" = "true" ] && just _stop_db; \
    exit $status

# Создать новую миграцию
migrate-new msg:
    @docker compose {{ compose }} run --rm backend alembic revision --autogenerate -m "{{ msg }}"

# Откатить последнюю миграцию
migrate-down:
    @started=$(just _ensure_db); \
    docker compose {{ compose }} run --rm backend alembic downgrade -1; status=$?; \
    [ "$started" = "true" ] && just _stop_db; \
    exit $status

# Показать текущую миграцию
migrate-current:
    @started=$(just _ensure_db); \
    docker compose {{ compose }} run --rm backend alembic current; status=$?; \
    [ "$started" = "true" ] && just _stop_db; \
    exit $status

# -------------------- Очистка --------------------
clean:
    @read -p "❗ Это удалит ВСЕ данные! Продолжить? (y/n) " confirm; \
    [ "$confirm" = "y" ] && docker compose {{ compose }} down -v && echo "✅" || echo "❌"

# -------------------- Приватные рецепты --------------------
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
