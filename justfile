# -------------------- Переменные --------------------
compose := "-f compose.base.yml -f compose.dev.yml"
backend_path := "backend/services"

# -------------------- Основные команды --------------------
# Список всех команд
default:
    @echo 'Доступные команды:'
    @echo ''
    @echo 'Запуск и остановка:'
    @echo '  just up [args]             - Запустить проект (пример: just up, just up -d, just up --build)'
    @echo '  just down                  - Остановить проект'
    @echo '  just restart               - Перезапустить проект'
    @echo '  just ps                    - Список контейнеров'
    @echo ''
    @echo 'Логи и отладка:'
    @echo '  just logs [service]        - Показать логи (пример: just logs, just logs auth)'
    @echo '  just logs-f [service]      - Следить за логами'
    @echo '  just shell service       	- Войти в контейнер'
    @echo '  just exec service [cmd]  	- Выполнить команду (пример: just exec auth "python -m app.migrate")'
    @echo ''
    @echo 'Разработка:'
    @echo '  just tests [args]          - Запустить тесты (пример: just tests, just tests --build)'
    @echo ''
    @echo 'Базы данных:'
    @echo '  just backup                - Сделать бэкап всех БД'
    @echo '  just restore-latest        - Восстановить все БД из последнего бэкапа'
    @echo '  just backup-del [keep=5]   - Удалить бэкапы (пример: just backup-del, just backup-del 0)'
    @echo ''
    @echo 'Миграции:'
    @echo '  just migrate [service]     - Применить миграции (пример: just migrate, just migrate auth)'
    @echo '  just migrate-new service [msg] - Создать миграцию'
    @echo '  just migrate-down service - Откатить миграцию'
    @echo ''
    @echo 'Очистка:'
    @echo '  just clean                 - Остановить и удалить данные'

# -------------------- Запуск и остановка --------------------
# Запустить проект
up *args:
	@docker compose {{compose}} up {{args}}

# Остановить проект
down:
	@docker compose {{compose}} down

# Перезапустить проект
restart:
	@docker compose {{compose}} restart

# Список контейнеров
ps:
	@docker compose {{compose}} ps

# -------------------- Логи --------------------
# Показать логи
logs service="":
	@docker compose {{compose}} logs {{service}}

# Следить за логами
logs-f service="":
	@docker compose {{compose}} logs -f {{service}}

# -------------------- Доступ к контейнерам --------------------
# Войти в контейнер
shell service:
	@just _ensure_app {{service}}
	@docker compose {{compose}} exec {{service}} sh

# Выполнить команду
exec service cmd:
	@just _ensure_app {{service}}
	@docker compose {{compose}} exec {{service}} {{cmd}}

# -------------------- Разработка --------------------
# Запустить все тесты
tests *args:
	@echo "🧪 Запуск тестов..."
	@services=$(just _get_services); \
	for s in $services; do \
		printf "  📦 %-20s" "$s..."; \
		[ "$(just _service_ready $s)" = "true" ] || { echo "❗ сервис не настроен"; continue; }; \
		[ "$(just _service_has_tests $s)" = "true" ] || { echo "❗ нет тестов"; continue; }; \
		just _run_in_service $s "tests {{args}}"; \
	done

# -------------------- Базы данных --------------------
# Бэкап всех БД
backup:
	@echo "💾 Создание бэкапов..."
	@services=$(just _get_services); \
	for s in $services; do \
		printf "  📦 %-20s" "$s..."; \
		[ "$(just _service_ready $s)" = "true" ] || { echo "❗ сервис не настроен"; continue; }; \
		just _run_in_service $s backup; \
	done

# Восстановить всех БД из бэкапов
restore-latest:
	@echo "💾 Восстановление из бэкапов..."
	@services=$(just _get_services); \
	for s in $services; do \
		printf "  📦 %-20s" "$s..."; \
		[ "$(just _service_ready $s)" = "true" ] || { echo "❗ сервис не настроен"; continue; }; \
		[ "$(just _service_has_backups $s)" = "true" ] || { echo "❗ нет бэкапов"; continue; }; \
		just _run_in_service $s restore-latest; \
	done

# Удалить бэкапы
backup-del keep="5":
	@echo "🧹 Очистка бэкапов..."; \
	services=$(just _get_services); \
	for s in $services; do \
		printf "  📦 %-20s" "$s..."; \
		[ "$(just _service_ready $s)" = "true" ] || { echo "❗ сервис не настроен"; continue; }; \
		[ "$(just _service_has_backups $s)" = "true" ] || { echo "❗ нет бэкапов"; continue; }; \
		just _run_in_service $s "backup-del '{{keep}}'"; \
	done

# -------------------- Миграции --------------------
# Применить миграции
migrate service="":
	@echo "📊 Применение миграций..."; \
	[ "{{service}}" = "" ] && services=$(just _get_services) || services="{{service}}"; \
	for s in $services; do \
		printf "  📦 %-20s" "$s..."; \
		[ "$(just _service_ready $s)" = "true" ] || { echo "❗ сервис не настроен"; continue; }; \
		just _run_in_service $s migrate; \
	done

# Создать миграцию
migrate-new service msg:
	@echo "📊 Создание миграции..."; \
	printf "  📦 %-20s" "{{service}}..."; \
	[ "$(just _service_ready "{{service}}")" = "true" ] || { echo "❗ сервис не настроен"; exit 0; }; \
	just _run_in_service {{service}} "migrate-new '{{msg}}'"

# Откатить миграцию
migrate-down service:
	@echo "📊 Откат миграции..."; \
	printf "  📦 %-20s" "{{service}}..."; \
	[ "$(just _service_ready "{{service}}")" = "true" ] || { echo "❗ сервис не настроен"; exit 0; }; \
	just _run_in_service {{service}} migrate-down

# -------------------- Очистка --------------------
# Остановить и удалить данные
clean:
	@read -p "❗ Это удалит ВСЕ данные! Продолжить? (y/n) " confirm; \
	[ "$confirm" = "y" ] && docker compose {{compose}} down -v && echo "✅" || echo "❌"

# -------------------- Приватные рецепты --------------------
_service_has_tests service:
	@cd "{{backend_path}}/{{service}}" && just _has_tests

_service_has_backups service:
	@cd "{{backend_path}}/{{service}}" && just _has_backups

_get_services:
	@ls -1 {{backend_path}}

_run_in_service service cmd:
	@cd "{{backend_path}}/{{service}}" && just {{cmd}} >/dev/null 2>&1 && echo "✅" || echo "❌"

_ensure_app service:
	@docker compose {{compose}} ps --status running | grep -q {{service}} || \
		docker compose {{compose}} up -d {{service}} > /dev/null 2>&1

_service_ready service:
	@path="{{backend_path}}/{{service}}"; \
	[ -d "$path" ] || { echo "false"; exit 0; }; \
	[ -f "$path/justfile" ] || { echo "false"; exit 0; }; \
	echo "true"
