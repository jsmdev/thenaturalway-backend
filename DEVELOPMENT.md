# Guía de Desarrollo

## Índice

1. [Initial Project Setup (Nuevos Proyectos)](#initial-project-setup-nuevos-proyectos)
2. [Setup Inicial (Proyectos Existentes)](#setup-inicial-proyectos-existentes)
3. [Herramientas de Desarrollo](#herramientas-de-desarrollo)
4. [Workflow de Desarrollo](#workflow-de-desarrollo)
5. [Convenciones de Código](#convenciones-de-código)
6. [Configuración de Editores](#configuración-de-editores)
7. [Solución de Problemas](#solución-de-problemas)

---

## Initial Project Setup (Nuevos Proyectos)

**Esta sección es para configurar un nuevo proyecto desde cero**. Si estás trabajando en este proyecto existente, ve a [Setup Inicial (Proyectos Existentes)](#setup-inicial-proyectos-existentes).

### Prerrequisitos

- Python 3.13+
- Git
- pip (package manager)
- Virtualenv o similar (recomendado)

### 1. Crear Estructura del Proyecto

```bash
# Crear directorio del proyecto
mkdir my-django-project
cd my-django-project

# Inicializar Git
git init

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar Django y DRF
pip install django djangorestframework
django-admin startproject config .
```

### 2. Configurar Herramientas de Calidad de Código

#### 2.1. Crear `requirements-dev.txt`

```txt
# Linting y Formatting
ruff>=0.1.9

# Pre-commit hooks
pre-commit>=3.5.0

# Testing
coverage>=7.3.0
factory-boy>=3.3.0

# Security
detect-secrets>=1.4.0

# Django-specific tools
django-upgrade>=1.15.0
```

#### 2.2. Crear `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "DJ",   # flake8-django
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "Q",    # flake8-quotes
    "S",    # bandit (security)
    "T20",  # flake8-print
    "RUF",  # ruff-specific rules
]

ignore = [
    "E501",   # Line too long (handled by formatter)
    "S101",   # Use of assert (needed in tests)
]

[tool.ruff.lint.per-file-ignores]
"**/tests.py" = ["S101"]  # Allow assert in tests
"**/migrations/*.py" = ["ALL"]  # Don't lint migrations

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"

[tool.ruff.lint.isort]
known-first-party = ["apps", "config"]
section-order = [
    "future",
    "standard-library",
    "django",
    "third-party",
    "first-party",
    "local-folder",
]

[tool.ruff.lint.isort.sections]
django = ["django"]
```

#### 2.3. Crear `.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
max_line_length = 100

[*.{json,yml,yaml}]
indent_style = space
indent_size = 2

[Makefile]
indent_style = tab
```

#### 2.4. Crear `.pre-commit-config.yaml`

```yaml
repos:
  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: mixed-line-ending
      - id: debug-statements

  # Ruff (linter + formatter)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # Security
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # Django-specific
  - repo: https://github.com/adamchainz/django-upgrade
    rev: 1.15.0
    hooks:
      - id: django-upgrade
        args: [--target-version, "5.1"]
```

#### 2.5. Crear `Makefile`

```makefile
.PHONY: help install-dev format check lint test coverage pre-commit clean

help:
	@echo "Available commands:"
	@echo "  make install-dev       - Install development dependencies"
	@echo "  make format            - Format code with Ruff"
	@echo "  make check             - Check code without modifying"
	@echo "  make lint              - Run linter only"
	@echo "  make test              - Run all tests"
	@echo "  make coverage          - Run tests with coverage report"
	@echo "  make pre-commit        - Run pre-commit hooks manually"
	@echo "  make pre-commit-update - Update pre-commit hooks"
	@echo "  make clean             - Clean temporary files"

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

format:
	ruff format .
	ruff check --fix .

check:
	ruff check .
	ruff format --check .

lint:
	ruff check .

test:
	python manage.py test

coverage:
	coverage run --source='.' manage.py test
	coverage report
	coverage html
	@echo "Coverage report: htmlcov/index.html"

pre-commit:
	pre-commit run --all-files

pre-commit-update:
	pre-commit autoupdate

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
```

### 3. Instalar y Configurar Herramientas

```bash
# Instalar dependencias de desarrollo
make install-dev
# o manualmente:
pip install -r requirements-dev.txt
pre-commit install

# Configurar Git para finales de línea
git config core.autocrlf input
git config core.eol lf

# Inicializar baseline de secretos
detect-secrets scan > .secrets.baseline
```

### 4. Crear `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/

# Django
*.log
db.sqlite3
media/
staticfiles/

# Testing
.coverage
htmlcov/
.pytest_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Secrets
.secrets.baseline
.env
```

### 5. Verificar Configuración

```bash
# Ejecutar pre-commit en todo el proyecto
make pre-commit

# Verificar que no hay errores de linting
make check

# Todo debería pasar sin errores
```

### 6. Primer Commit

```bash
git add .
git commit -m "chore: initial project setup with linting and pre-commit"
```

### Opciones de Personalización

#### Cambiar Longitud de Línea

En `pyproject.toml`:
```toml
[tool.ruff]
line-length = 120  # Default: 88 (Black), este proyecto usa 100
```

#### Agregar/Quitar Reglas de Ruff

En `pyproject.toml`:
```toml
[tool.ruff.lint]
select = ["ALL"]  # Activar todas las reglas
ignore = ["D"]    # Desactivar docstring checks
```

#### Desactivar Hooks Específicos

En `.pre-commit-config.yaml`, comentar el hook:
```yaml
# - id: detect-secrets  # Desactivado temporalmente
```

### Recursos para Nuevos Proyectos

- **[docs/LINTING_AND_PRECOMMIT_GUIDE.md](docs/LINTING_AND_PRECOMMIT_GUIDE.md)**: Guía completa y didáctica
- **[Ruff Documentation](https://docs.astral.sh/ruff/)**: Documentación oficial
- **[Pre-commit Hooks](https://pre-commit.com/hooks.html)**: Hooks disponibles
- **[EditorConfig](https://editorconfig.org/)**: Especificación completa

---

## Setup Inicial (Proyectos Existentes)

**Esta sección es para desarrolladores que se unen a este proyecto existente**.

### 1. Instalar Dependencias

```bash
# Dependencias de producción
pip install -r requirements.txt

# Dependencias de desarrollo
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install
```

### 2. Configurar Git

```bash
# Configurar finales de línea
git config core.autocrlf input
git config core.eol lf
```

### 3. Inicializar Baseline de Secretos

```bash
# Primera vez - crear baseline
detect-secrets scan > .secrets.baseline

# Auditar secretos detectados
detect-secrets audit .secrets.baseline
```

## Herramientas de Desarrollo

**Para información detallada** sobre estas herramientas, su funcionamiento, ventajas/desventajas, y mejores prácticas, consulta: **[docs/LINTING_AND_PRECOMMIT_GUIDE.md](docs/LINTING_AND_PRECOMMIT_GUIDE.md)**

### Ruff (Linter y Formatter)

Ruff es un linter y formatter ultra-rápido para Python que reemplaza a:
- **Black** (formatter)
- **isort** (ordenamiento de imports)
- **flake8** (linter)
- **pylint** (linter)
- Y más...

**Comandos**:

```bash
# Verificar código sin modificar
make check
# o
ruff check apps config
ruff format --check apps config

# Formatear código automáticamente
make format
# o
ruff format apps config
ruff check --fix apps config

# Solo linter
make lint
# o
ruff check apps config
```

**Configuración**: Ver `pyproject.toml`

### Pre-commit Hooks

Los hooks se ejecutan automáticamente antes de cada commit:

- Eliminar espacios en blanco al final
- Agregar línea en blanco al final de archivo
- Verificar sintaxis YAML/JSON/TOML
- Prevenir archivos grandes
- Verificar conflictos de merge
- **Ruff linter** (con fix automático)
- **Ruff formatter**
- Detectar secretos
- Actualizar sintaxis Django

**Comandos**:

```bash
# Ejecutar manualmente en todos los archivos
make pre-commit
# o
pre-commit run --all-files

# Actualizar a versiones más recientes
make pre-commit-update
# o
pre-commit autoupdate

# Saltarse hooks en un commit (NO RECOMENDADO)
git commit --no-verify
```

### Testing

```bash
# Ejecutar todos los tests
make test
# o
docker compose run --rm web python manage.py test

# Ejecutar tests de una app específica
make test-app APP=routines
# o
docker compose run --rm web python manage.py test apps.routines

# Generar reporte de cobertura
make coverage
# Ver htmlcov/index.html en el navegador
```

### Comandos Django

```bash
# System checks
make django-check

# Migraciones
make migrations
make migrate

# Shell
make shell
```

## Workflow de Desarrollo

### 1. Antes de Comenzar a Trabajar

```bash
# Asegurarse de tener las últimas dependencias
pip install -r requirements-dev.txt
pre-commit install
```

### 2. Durante el Desarrollo

```bash
# Formatear código automáticamente
make format

# Verificar que todo esté correcto
make check

# Ejecutar tests relacionados
make test-app APP=nombre_app
```

### 3. Antes de Hacer Commit

Los pre-commit hooks se ejecutarán automáticamente, pero puedes ejecutarlos manualmente:

```bash
# Ejecutar todos los checks
make pre-commit

# Si todo pasa, hacer commit
git add .
git commit -m "tipo: mensaje"
```

### 4. Formato de Commits

Seguir [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(alcance): descripción

Tipos: feat, fix, docs, style, refactor, test, chore
```

Ejemplos:
```
feat(users): agregar endpoint de registro
fix(routines): corregir validación de semanas
test(exercises): agregar tests de cascade delete
docs: actualizar README con instrucciones
```

## Convenciones de Código

### Python/Django

- **Longitud de línea**: 100 caracteres
- **Estilo de comillas**: Dobles (`"`)
- **Ordenamiento de imports**: automático con Ruff (isort)
- **Formato de código**: automático con Ruff (black-compatible)
- **Type hints**: obligatorios en funciones nuevas
- **Docstrings**: Google style

### Imports

Orden automático (configurado en `pyproject.toml`):
1. Future imports (`from __future__ import annotations`)
2. Standard library
3. Django
4. Third-party
5. First-party (apps, config)
6. Local folder

### Tests

- Seguir patrón **Arrange-Act-Assert (AAA)**
- Usar `@classmethod setUpTestData()` para datos inmutables
- Usar mocks en tests de servicios
- Usar `reverse()` para URLs
- SubTests para múltiples aserciones

Ver `.ai/craftsman/c-1.test.instructions.v2.md` para guía completa.

## Configuración de Editores

### VS Code

Instalar extensiones:
- Python
- Ruff
- EditorConfig

Configuración (`.vscode/settings.json`):
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "ruff.lint.run": "onSave"
}
```

### PyCharm

1. Instalar plugin de Ruff
2. Habilitar EditorConfig
3. Configurar Ruff como formatter externo

## Solución de Problemas

### Pre-commit Falla

```bash
# Ver qué falló
pre-commit run --all-files

# Limpiar caché y reinstalar
pre-commit clean
pre-commit install --install-hooks
```

### Ruff Encuentra Muchos Errores

```bash
# Intentar fix automático primero
ruff check --fix apps config

# Ver errores que no se pueden arreglar automáticamente
ruff check apps config
```

### Tests Fallan

```bash
# Limpiar base de datos de test
docker compose down -v
docker compose up -d db

# Ejecutar migraciones
make migrate

# Ejecutar tests nuevamente
make test
```

## Enlaces Útiles

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Django Coding Style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
