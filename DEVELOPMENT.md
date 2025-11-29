# Guía de Desarrollo

## Setup Inicial

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
