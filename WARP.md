# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**The Natural Way** is a Django REST Framework backend API for a fitness tracking application. Users can create custom workout routines, log training sessions, and monitor their progress over time.

**Stack**: Python 3.13, Django 5.1+, Django REST Framework, JWT authentication, SQLite (dev) / PostgreSQL (prod)

## Common Commands

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# View available commands
make help
```

### Code Quality
```bash
# Format code automatically (Ruff)
make format

# Check code without modifying
make check

# Run linter
make lint

# Run pre-commit hooks manually
make pre-commit
```

### Development Server
```bash
# Run migrations and start development server
python manage.py migrate
python manage.py runserver

# Or using Docker
docker compose up
```

### Database Operations
```bash
# Create migrations after model changes
make migrations

# Apply migrations
make migrate

# Create superuser
python manage.py createsuperuser
```

### Testing
```bash
# Run all tests
make test

# Run tests for specific app
make test-app APP=users

# Generate coverage report
make coverage
```

### Django Shell
```bash
# Access Django shell for debugging
make shell
```

## Architecture

### Three-Layer Architecture

The codebase follows a strict three-layer architecture:

```
Request → View → Service → Repository → Database
Response ← View ← Service ← Repository ← Database
```

**Dependency Rules**:
- Views depend on Services
- Services depend on Repositories  
- Repositories interact with Models/ORM
- **Never** invert these dependencies
- Only one level of dependencies (don't skip layers)

### App Structure

Each Django app in `apps/` follows this structure:
- `views.py` - HTTP request/response handling, API endpoints
- `serializers.py` - Data validation and transformation
- `services.py` - Business logic and orchestration
- `repositories.py` - Data access layer (database queries)
- `models.py` - Django ORM models
- `urls.py` - URL routing

**Example**: `apps/users/` implements user registration, authentication, and profile management using this pattern.

### Response Format Standards

**Success Response**:
```python
{
    "data": {...},           # Main response data
    "message": "...",        # Optional success message
    "request": {             # Optional request metadata
        "method": "GET",
        "path": "/api/...",
        "host": "..."
    }
}
```

**Error Response**:
```python
{
    "error": "Error type",   # Error category
    "message": "...",        # Human-readable error message
    "request": {...}         # Optional request metadata
}
```

### Authentication

- JWT authentication using `djangorestframework-simplejwt`
- Access token lifetime: 60 minutes
- Refresh token lifetime: 7 days
- Token rotation enabled with blacklist after rotation
- Custom user model: `apps.users.models.User` (extends `AbstractBaseUser`)

## Code Style and Conventions

**Important**: Code style is enforced automatically by Ruff (linter/formatter) and pre-commit hooks.

### Automated Tools

- **Ruff**: Linter and formatter (replaces Black, isort, flake8, pylint)
- **Pre-commit hooks**: Run automatically before each commit
- **Configuration**: `pyproject.toml` and `.pre-commit-config.yaml`
- **EditorConfig**: `.editorconfig` for cross-editor consistency

**For detailed information** about these tools, how they work, and best practices, see `docs/LINTING_AND_PRECOMMIT_GUIDE.md`.

### Import Organization

Imports are automatically ordered by Ruff (isort):

```python
from __future__ import annotations

from typing import TYPE_CHECKING

# Standard library imports
import os
from datetime import datetime

# Django imports
from django.db import models

# Django REST Framework imports
from rest_framework.views import APIView
from rest_framework.response import Response

# Third-party imports
import requests

# Local imports
from apps.users.services import register_user_service
from apps.users.serializers import UserSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
```

### Style Guidelines

- **Line length**: 100 characters (enforced by Ruff)
- **Indentation**: 4 spaces for Python
- **Quotes**: Double quotes for strings
- **Line endings**: LF (Unix-style)

### Naming Conventions

- Functions/methods: `snake_case` with verb prefix (`get_user`, `create_order`)
- Classes: `PascalCase` (`UserService`, `PaymentProcessor`)
- Constants: `UPPER_SNAKE_CASE` 
- Files: `snake_case.py`
- Boolean variables: `is_active`, `has_permission`, `can_edit`

### Type Hints
- Use type hints for all function parameters and return values
- Use `typing.Optional` for nullable values
- Use `typing.TYPE_CHECKING` for imports only needed for type hints
- Avoid `Any` unless absolutely necessary

### Function Design
- Keep functions small (<20 lines ideally, max 50)
- One function, one responsibility
- Use early returns for validation
- Separate pure functions from side effects
- Max 3-4 parameters (use dataclasses/dicts for more)

### Clean Code Principles
- **YAGNI**: Don't implement until needed
- **KISS**: Simplest solution that works
- **DRY**: Extract common logic to reusable functions
- **SOLID**: Single responsibility, depend on abstractions
- Use descriptive names that reveal intent
- Avoid magic numbers - use named constants

## Development Workflow

### AI-Driven Development Methodology

This project follows the AIDD methodology defined in `.ai/AIDD.metodology.md`:

**Architect Phase**:
- Input: PRD, domain model, and feature templates in `.ai/architect/`
- Output: `docs/PRD.md`, `docs/DOMAIN.md`, GitHub issues

**Builder Phase**:
- Input: Feature plans in `.ai/builder/`, coding rules in `.cursor/rules/`
- Output: Implementation plans in `docs/features/`, source code in `apps/`

**Craftsman Phase**:  
- Input: Test instructions in `.ai/craftsman/`
- Output: Tests in `apps/*/tests.py`, documentation

### Project Documentation

- `docs/PRD.md` - Product requirements and features
- `docs/DOMAIN.md` - Domain model with entities and relationships
- `docs/features/*/plan.md` - Implementation plans for specific features
- `.cursor/rules/*.mdc` - Coding standards and patterns (Django/DRF specific)

### Adding New Features

1. Review the feature description in `docs/PRD.md`
2. Check domain model in `docs/DOMAIN.md` for data structures
3. Follow three-layer architecture pattern (View → Service → Repository)
4. Reference `.cursor/rules/django-drf-api.rules.mdc` for code patterns
5. Apply clean code principles from `.cursor/rules/clean-code-django-python.mdc`
6. Write tests in `apps/*/tests.py`

### Settings Configuration

- Development settings: `config/settings.py`
- Secret key: Change in production (currently using dev key)
- Database: SQLite for dev (in `db.sqlite3`), configured for PostgreSQL in prod
- Allowed hosts: Set via `DJANGO_ALLOWED_HOSTS` environment variable

## Django REST Framework Patterns

### ViewSets vs APIView
- Use `APIView` for custom endpoints with specific logic (current pattern)
- Use `ModelViewSet` for standard CRUD operations when appropriate

### Serializers
- Use `ModelSerializer` for Django models
- Define `Meta.fields` explicitly (avoid `__all__`)
- Custom validation: `validate_<field>()` methods
- Computed fields: `SerializerMethodField()`

### Permissions
- Default: `AllowAny` (override per view)
- Use `IsAuthenticated` for protected endpoints
- Create custom permission classes in `apps/*/permissions.py` as needed

## Development Tools

### Linting and Formatting

- **Ruff**: Ultra-fast linter and formatter
  - Configuration: `pyproject.toml`
  - Run: `make format` or `make check`
  - Replaces: Black, isort, flake8, pylint, pyupgrade

### Pre-commit Hooks

- Automatically run before each commit
- Configuration: `.pre-commit-config.yaml`
- Install: `pre-commit install`
- Run manually: `make pre-commit`

### Testing Tools

- Django TestCase
- factory-boy for test data
- coverage for test coverage reports
- See: `.ai/craftsman/c-1.test.instructions.v2.md`

### Documentation

- **DEVELOPMENT.md**: Complete development guide
- **docs/LINTING_AND_PRECOMMIT_GUIDE.md**: Comprehensive guide to linting and pre-commit tools
- **Makefile**: List of available commands (`make help`)
- **pyproject.toml**: Tool configurations
- **.editorconfig**: Editor consistency

## Important Notes

- Custom user model is `apps.users.models.User` (not Django's default)
- `AUTH_USER_MODEL = 'users.User'` set in settings
- JWT tokens are managed by `rest_framework_simplejwt`
- Database currently uses SQLite; PostgreSQL support configured but commented in docker-compose
- All API endpoints are under `/api/` prefix
- The project uses absolute imports for app modules
- **Code style is automatically enforced** by Ruff and pre-commit hooks
