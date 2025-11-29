.PHONY: help install install-dev lint format check test coverage pre-commit clean

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias de producción
	pip install -r requirements.txt

install-dev: ## Instalar dependencias de desarrollo
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

lint: ## Ejecutar linter (Ruff)
	@echo "🔍 Ejecutando linter..."
	ruff check apps config

format: ## Formatear código automáticamente
	@echo "✨ Formateando código..."
	ruff format apps config
	ruff check --fix apps config

check: ## Verificar código sin modificar
	@echo "🔍 Verificando código..."
	ruff check apps config
	ruff format --check apps config

test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	docker compose run --rm web python manage.py test

test-app: ## Ejecutar tests de una app específica (uso: make test-app APP=routines)
	@echo "🧪 Ejecutando tests de apps.$(APP)..."
	docker compose run --rm web python manage.py test apps.$(APP)

coverage: ## Generar reporte de cobertura
	@echo "📊 Generando reporte de cobertura..."
	docker compose run --rm web coverage run --source='apps' manage.py test
	docker compose run --rm web coverage report
	docker compose run --rm web coverage html
	@echo "✅ Reporte HTML generado en htmlcov/index.html"

pre-commit: ## Ejecutar pre-commit en todos los archivos
	@echo "🔨 Ejecutando pre-commit hooks..."
	pre-commit run --all-files

pre-commit-update: ## Actualizar pre-commit hooks
	@echo "🔄 Actualizando pre-commit hooks..."
	pre-commit autoupdate

secrets-scan: ## Escanear secretos en el código
	@echo "🔐 Escaneando secretos..."
	detect-secrets scan --baseline .secrets.baseline

secrets-audit: ## Auditar secretos detectados
	@echo "🔍 Auditando secretos..."
	detect-secrets audit .secrets.baseline

django-check: ## Ejecutar checks de Django
	@echo "✅ Ejecutando Django system checks..."
	docker compose run --rm web python manage.py check

django-upgrade: ## Actualizar sintaxis de Django
	@echo "⬆️  Actualizando código Django..."
	django-upgrade --target-version 5.1 apps/**/*.py config/**/*.py

migrations: ## Crear migraciones
	@echo "📝 Creando migraciones..."
	docker compose run --rm web python manage.py makemigrations

migrate: ## Aplicar migraciones
	@echo "🚀 Aplicando migraciones..."
	docker compose run --rm web python manage.py migrate

shell: ## Abrir shell de Django
	docker compose run --rm web python manage.py shell

clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "✅ Limpieza completada"

.DEFAULT_GOAL := help
