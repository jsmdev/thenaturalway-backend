# The Natural Way - Backend API

API backend para aplicación de fitness tracking desarrollada con Django REST Framework.

## 🚀 Quick Start

### 1. Clonar y Preparar Entorno

```bash
# Clonar repositorio
git clone <repo-url>
cd thenaturalway-backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install
```

### 2. Configurar Base de Datos

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 3. Arrancar Servidor

```bash
# Servidor de desarrollo
python manage.py runserver

# O usando Makefile
make run
```

El servidor estará disponible en: http://127.0.0.1:8000/

## 📋 Estructura de Requirements

- **`requirements.txt`**: Dependencias de producción (Django, DRF, psycopg2, etc.)
- **`requirements-dev.txt`**: Dependencias de desarrollo (Ruff, pytest, pre-commit, etc.)

**Instalación completa:**
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

## 🛠️ Comandos Disponibles

### Usando Makefile

```bash
make help              # Ver todos los comandos disponibles
make format            # Formatear código con Ruff
make check             # Verificar código sin modificar
make lint              # Solo linter
make test              # Ejecutar tests
make coverage          # Tests con reporte de cobertura
make pre-commit        # Ejecutar pre-commit hooks
make migrations        # Crear migraciones
make migrate           # Aplicar migraciones
make shell             # Django shell
```

### Usando Cursor/VS Code Tasks

Presiona `Cmd+Shift+P` (Mac) o `Ctrl+Shift+P` (Windows/Linux) y busca "Tasks: Run Task":

- **Django: Run Server** - Arrancar servidor de desarrollo
- **Django: Run All Tests** - Ejecutar todos los tests
- **Django: Make Migrations** - Crear migraciones
- **Django: Migrate** - Aplicar migraciones
- **Ruff: Format Code** - Formatear código
- **Ruff: Lint Code** - Verificar código
- Y más...

## 🏗️ Arquitectura

El proyecto sigue una arquitectura en 3 capas:

```
Request → View → Service → Repository → Database
Response ← View ← Service ← Repository ← Database
```

Cada app en `apps/` tiene:
- `views.py` - Endpoints API (HTTP request/response)
- `serializers.py` - Validación y transformación de datos
- `services.py` - Lógica de negocio
- `repositories.py` - Acceso a datos
- `models.py` - Modelos Django ORM

## 📚 Documentación

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guía completa de desarrollo
- **[WARP.md](WARP.md)** - Guía para WARP AI
- **[docs/LINTING_AND_PRECOMMIT_GUIDE.md](docs/LINTING_AND_PRECOMMIT_GUIDE.md)** - Guía de linting y pre-commit
- **[docs/PRD.md](docs/PRD.md)** - Product Requirements Document
- **[docs/DOMAIN.md](docs/DOMAIN.md)** - Modelo de dominio

## 🧪 Testing

```bash
# Todos los tests
make test

# Tests de una app específica
make test-app APP=users

# Con cobertura
make coverage
```

Los tests siguen el patrón Arrange-Act-Assert (AAA). Ver `.ai/craftsman/c-1.test.instructions.v2.md` para guía completa.

## 🎨 Code Style

El proyecto usa **Ruff** para linting y formatting:

- **Line length**: 100 caracteres
- **Quotes**: Dobles (`"`)
- **Indentation**: 4 espacios
- **Pre-commit hooks**: Ejecutan automáticamente en cada commit

```bash
# Formatear código
make format

# Verificar código
make check
```

Ver `docs/LINTING_AND_PRECOMMIT_GUIDE.md` para más información.

## 🔐 Autenticación

El proyecto usa JWT authentication:
- Access token: 60 minutos
- Refresh token: 7 días
- Endpoints: `/api/token/`, `/api/token/refresh/`

## 🗂️ Apps Principales

- **users** - Gestión de usuarios y autenticación
- **exercises** - Biblioteca de ejercicios
- **routines** - Rutinas de entrenamiento personalizadas

## 🐳 Docker (Opcional)

```bash
# Arrancar con Docker
docker compose up

# Ejecutar comandos en contenedor
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py test
```

## 📝 Conventional Commits

El proyecto usa [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(scope): descripción

Tipos: feat, fix, docs, style, refactor, test, chore
```

Ejemplos:
```
feat(users): agregar endpoint de registro
fix(routines): corregir validación de semanas
test(exercises): agregar tests de cascade delete
```

## 🤝 Contribuir

1. Crear rama desde `main`
2. Hacer cambios siguiendo las convenciones
3. Ejecutar `make format` y `make test`
4. Hacer commit siguiendo Conventional Commits
5. Push y crear Pull Request

Los pre-commit hooks se ejecutarán automáticamente y verificarán:
- Formato de código (Ruff)
- Linting (Ruff)
- Detección de secretos
- Sintaxis YAML/JSON/TOML
- Y más...

## 📞 Stack Técnico

- **Python**: 3.13+
- **Django**: 5.1+
- **Django REST Framework**: 3.15+
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Linting/Formatting**: Ruff
- **Testing**: Django TestCase + factory-boy
- **Pre-commit**: detect-secrets, django-upgrade, ruff

## 📄 Licencia

[Especificar licencia]

## 👥 Equipo

[Información del equipo]
