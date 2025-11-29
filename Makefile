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

test: ## Ejecutar tests (local)
	@echo "🧪 Ejecutando tests..."
	python manage.py test

test-docker: ## Ejecutar tests (Docker)
	@echo "🧪 Ejecutando tests con Docker..."
	docker compose run --rm web python manage.py test

test-app: ## Ejecutar tests de una app específica (uso: make test-app APP=routines)
	@echo "🧪 Ejecutando tests de apps.$(APP)..."
	python manage.py test apps.$(APP)

test-app-docker: ## Ejecutar tests de una app (Docker)
	@echo "🧪 Ejecutando tests de apps.$(APP) con Docker..."
	docker compose run --rm web python manage.py test apps.$(APP)

coverage: ## Generar reporte de cobertura (local)
	@echo "📊 Generando reporte de cobertura..."
	coverage run --source='apps' manage.py test
	coverage report
	@mkdir -p docs/quality-reports/coverage
	coverage html -d docs/quality-reports/coverage
	@echo "✅ Reporte HTML generado en docs/quality-reports/coverage/index.html"
	@open docs/quality-reports/coverage/index.html || xdg-open docs/quality-reports/coverage/index.html || true

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

django-check: ## Ejecutar checks de Django (local)
	@echo "✅ Ejecutando Django system checks..."
	python manage.py check

django-check-docker: ## Ejecutar checks de Django (Docker)
	@echo "✅ Ejecutando Django system checks con Docker..."
	docker compose run --rm web python manage.py check

django-upgrade: ## Actualizar sintaxis de Django
	@echo "⬆️  Actualizando código Django..."
	django-upgrade --target-version 5.1 apps/**/*.py config/**/*.py

migrations: ## Crear migraciones (local)
	@echo "📝 Creando migraciones..."
	python manage.py makemigrations

migrations-docker: ## Crear migraciones (Docker)
	@echo "📝 Creando migraciones con Docker..."
	docker compose run --rm web python manage.py makemigrations

migrate: ## Aplicar migraciones (local)
	@echo "🚀 Aplicando migraciones..."
	python manage.py migrate

migrate-docker: ## Aplicar migraciones (Docker)
	@echo "🚀 Aplicando migraciones con Docker..."
	docker compose run --rm web python manage.py migrate

shell: ## Abrir shell de Django (local)
	python manage.py shell

shell-docker: ## Abrir shell de Django (Docker)
	docker compose run --rm web python manage.py shell

run: ## Arrancar servidor de desarrollo
	@echo "🚀 Arrancando servidor de desarrollo..."
	python manage.py runserver

run-docker: ## Arrancar servidor con Docker
	@echo "🐳 Arrancando servidor con Docker..."
	docker compose up -d

stop-docker: ## Detener servidor Docker
	@echo "🛑 Deteniendo servidor Docker..."
	docker compose down

clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf docs/quality-reports
	@echo "✅ Limpieza completada"

quality: ## Análisis exhaustivo de calidad de código
	@echo "🔍 Análisis exhaustivo de calidad..."
	@mkdir -p docs/quality-reports/code-analysis
	@echo "⚙️  Ejecutando Ruff..."
	@ruff check apps config --output-format=json > docs/quality-reports/code-analysis/ruff.json || true
	@echo "📊 Analizando complejidad (Radon)..."
	@radon cc apps/ -a -j > docs/quality-reports/code-analysis/complexity.json
	@radon mi apps/ -j > docs/quality-reports/code-analysis/maintainability.json
	@echo "🔒 Análisis de seguridad (Bandit)..."
	@bandit -r apps/ -f json -o docs/quality-reports/code-analysis/security.json || true
	@echo "🔍 Linting exhaustivo (Pylint)..."
	@pylint apps/ --output-format=json > docs/quality-reports/code-analysis/pylint.json || true
	@echo "💀 Detectando código muerto (Vulture)..."
	@vulture apps/ --min-confidence 80 > docs/quality-reports/code-analysis/dead-code.txt || true
	@echo "✅ Análisis completo! Reportes en: docs/quality-reports/code-analysis/"
	@echo "   - ruff.json: Problemas de estilo y bugs"
	@echo "   - complexity.json: Complejidad ciclomática"
	@echo "   - maintainability.json: Índice de mantenibilidad"
	@echo "   - security.json: Vulnerabilidades de seguridad"
	@echo "   - pylint.json: Linting exhaustivo"
	@echo "   - dead-code.txt: Código muerto/no usado"

quality-summary: ## Resumen rápido de calidad
	@echo "📊 Resumen de calidad de código"
	@echo "=== Complejidad ==="
	@radon cc apps/ -a -s
	@echo "=== Mantenibilidad ==="
	@radon mi apps/ -s
	@echo "=== Seguridad (top 10) ==="
	@bandit -r apps/ -ll | head -20 || true
	@echo "=== Código muerto ==="
	@vulture apps/ --min-confidence 90 | head -20 || true

quality-html: ## Generar dashboard HTML visual
	@echo "🌐 Generando dashboard HTML..."
	@python scripts/generate_quality_dashboard.py
	@echo "✅ Dashboard listo en: docs/quality-reports/code-analysis/dashboard.html"
	@open docs/quality-reports/code-analysis/dashboard.html || xdg-open docs/quality-reports/code-analysis/dashboard.html || true

.DEFAULT_GOAL := help
