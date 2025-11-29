# Quick Start Guide - Guía de Comandos por Situación

Esta guía te dice **exactamente qué comandos ejecutar** en cada situación.

## 📋 Índice Rápido

- [Primera Vez en el Proyecto](#primera-vez-en-el-proyecto)
- [Día a Día: Empezar a Trabajar](#día-a-día-empezar-a-trabajar)
- [Desarrollando una Feature](#desarrollando-una-feature)
- [Antes de Hacer Commit](#antes-de-hacer-commit)
- [Cuando Hacer Migraciones](#cuando-hacer-migraciones)
- [Verificar Estado del Proyecto](#verificar-estado-del-proyecto)
- [Docker vs Local](#docker-vs-local)
- [Troubleshooting](#troubleshooting)

---

## Primera Vez en el Proyecto

### Escenario: Acabas de clonar el repositorio

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
source .venv/bin/activate  # Mac/Linux
# o en Windows:
# .venv\Scripts\activate

# 3. Instalar AMBOS requirements
pip install -r requirements.txt       # Producción (Django, DRF, etc.)
pip install -r requirements-dev.txt   # Desarrollo (Ruff, pytest, etc.)

# 4. Configurar pre-commit
pre-commit install

# 5. Aplicar migraciones
python manage.py migrate

# 6. (Opcional) Crear superusuario
python manage.py createsuperuser

# ✅ Listo! Ahora puedes arrancar:
python manage.py runserver
```

**¿O prefieres usar Cursor Task?**
- `Cmd+Shift+P` → "Tasks: Run Task" → **"Setup: Initial Project Setup"**
- Hace los pasos 3-5 automáticamente

---

## Día a Día: Empezar a Trabajar

### Escenario: Ya tienes todo instalado, es un nuevo día de trabajo

```bash
# 1. Activar entorno virtual (SIEMPRE primero)
source .venv/bin/activate

# 2. Actualizar código
git pull

# 3. ¿Hay nuevas dependencias? (si hubo cambios en requirements)
pip install -r requirements.txt -r requirements-dev.txt

# 4. ¿Hay nuevas migraciones? (si hubo cambios en models)
python manage.py migrate

# 5. Arrancar servidor
python manage.py runserver
# o
make run
# o Cursor Task: "Django: Run Server"
```

**Atajo rápido con verificación:**
```bash
source .venv/bin/activate
git pull
pip install -r requirements.txt -r requirements-dev.txt  # Solo si es necesario
python manage.py migrate  # Solo si es necesario
make run
```

---

## Desarrollando una Feature

### Escenario: Estás escribiendo código

**¿Cuándo ejecutar qué?**

| Situación | Comando |
|-----------|---------|
| Modificaste un modelo | `python manage.py makemigrations` |
| Después de makemigrations | `python manage.py migrate` |
| Quieres formatear código | `make format` o Task: "Ruff: Format Code" |
| Quieres verificar código | `make check` o Task: "Ruff: Lint Code" |
| Escribiste tests | `make test` o Task: "Django: Run All Tests" |
| Tests de una app | `make test-app APP=users` |
| Ver cobertura | `make coverage` |

**Workflow típico:**
```bash
# 1. Editar código
# ... haces cambios en apps/users/models.py

# 2. Si cambiaste models:
python manage.py makemigrations

# 3. Aplicar migraciones
python manage.py migrate

# 4. Formatear código
make format

# 5. Ejecutar tests
make test

# 6. Si todo OK → commit (ver siguiente sección)
```

---

## Antes de Hacer Commit

### Escenario: Quieres hacer commit de tus cambios

```bash
# Opción 1: Dejar que pre-commit lo haga automáticamente
git add .
git commit -m "feat(users): agregar validación de email"
# → Pre-commit ejecuta automáticamente: format, lint, secrets, etc.
# → Si pasa → commit OK
# → Si falla → corrige y vuelve a intentar

# Opción 2: Verificar manualmente ANTES del commit
make format      # Formatear
make check       # Verificar
make test        # Tests
git add .
git commit -m "..."

# Opción 3: Todo en uno (Cursor Task)
# Task: "Dev: Format, Lint and Test"
# Luego:
git add .
git commit -m "..."
```

**Si el commit falla por pre-commit:**
```bash
# 1. Ver qué falló (ya te lo muestra)
# 2. Corregir los errores
# 3. Agregar cambios nuevamente
git add .
# 4. Intentar commit otra vez
git commit -m "..."
```

---

## Cuando Hacer Migraciones

### ¿Cuándo ejecutar `makemigrations` y `migrate`?

**Ejecuta `makemigrations` SOLO cuando:**
- ✅ Creas un nuevo modelo
- ✅ Modificas campos de un modelo existente (agregar, eliminar, cambiar tipo)
- ✅ Cambias opciones de un modelo (verbose_name, ordering, etc.)
- ✅ Modificas relaciones (ForeignKey, ManyToMany, etc.)

**NO ejecutes `makemigrations` cuando:**
- ❌ Solo cambias métodos del modelo (`__str__`, `save()`, etc.)
- ❌ Cambias docstrings o comentarios
- ❌ Modificas views, serializers, services, repositories

**Después de `makemigrations`, SIEMPRE ejecuta `migrate`:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Verificar migraciones pendientes:**
```bash
python manage.py showmigrations
# ✅ [X] = aplicada
# ❌ [ ] = pendiente
```

---

## Verificar Estado del Proyecto

### ¿Cómo saber si tengo todo lo que necesito?

**Checklist completo:**

```bash
# 1. ¿Está activado el entorno virtual?
which python
# Debe mostrar: /Users/tu-usuario/.../thenaturalway-backend/.venv/bin/python
# Si no → source .venv/bin/activate

# 2. ¿Tengo todas las dependencias?
pip list | grep -E "(Django|ruff|pre-commit)"
# Debe mostrar: Django 5.1.x, ruff 0.x.x, pre-commit 3.x.x

# 3. ¿Están instalados los pre-commit hooks?
ls .git/hooks/pre-commit
# Si existe → OK
# Si no → pre-commit install

# 4. ¿Hay migraciones pendientes?
python manage.py showmigrations | grep "\[ \]"
# Si muestra algo → python manage.py migrate
# Si no muestra nada → OK

# 5. ¿Pasa el linter?
make check
# Si muestra errores → make format

# 6. ¿Pasan los tests?
make test
# Si fallan → revisar y corregir
```

**Comando rápido de verificación (Makefile):**
```bash
make help
# Muestra todos los comandos disponibles
```

---

## Docker vs Local

### ¿Cuándo usar Docker y cuándo local?

**Usa LOCAL cuando:**
- ✅ Desarrollo diario (más rápido)
- ✅ Debugging con breakpoints
- ✅ Usar Django shell (`python manage.py shell`)
- ✅ Ejecutar tests rápidamente

**Usa DOCKER cuando:**
- ✅ Necesitas PostgreSQL (producción-like)
- ✅ Pruebas de integración completas
- ✅ Quieres ambiente reproducible
- ✅ Onboarding de nuevo desarrollador

### Comandos equivalentes:

| Acción | Local | Docker |
|--------|-------|--------|
| Arrancar servidor | `make run` | `make run-docker` |
| Detener servidor | `Ctrl+C` | `make stop-docker` |
| Ejecutar tests | `make test` | `make test-docker` |
| Tests de una app | `make test-app APP=users` | `make test-app-docker APP=users` |
| Cobertura | `make coverage` | (usar local) |
| Crear migraciones | `make migrations` | `make migrations-docker` |
| Aplicar migraciones | `make migrate` | `make migrate-docker` |
| Django shell | `make shell` | `make shell-docker` |
| Django check | `make django-check` | `make django-check-docker` |

### Workflow recomendado:

**Desarrollo normal → LOCAL**
```bash
source .venv/bin/activate
make run
# Desarrollar...
make test
```

**Tests finales antes de PR → DOCKER**
```bash
make run-docker
# Verificar en ambiente similar a producción
make test  # con Docker compose
```

---

## Integrar Make en tu Flujo

### ¿Qué comandos usar del Makefile?

**Comandos esenciales:**

```bash
make help              # Ver todos los comandos (SIEMPRE útil)
make install-dev       # Instalar todo (primera vez)
make run               # Arrancar servidor local
make format            # Formatear código
make check             # Verificar sin modificar
make test              # Ejecutar tests
make test-app APP=users  # Tests de una app
make coverage          # Tests con cobertura
make migrations        # Crear migraciones
make migrate           # Aplicar migraciones
make shell             # Django shell
make clean             # Limpiar cache
```

**Workflow diario con Make:**

```bash
# Mañana
source .venv/bin/activate
make run              # Arrancar

# Desarrollo
make format           # Después de escribir código
make test-app APP=users  # Después de escribir tests

# Antes de commit
make format
make check
make test

# Commit
git add .
git commit -m "..."
```

---

## Troubleshooting

### Problema: "ruff: command not found"

**Causa:** No tienes instalados los requirements-dev.txt

**Solución:**
```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Problema: "No module named 'django'"

**Causa:** Entorno virtual no activado o sin dependencias

**Solución:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Problema: "Table doesn't exist"

**Causa:** No has aplicado las migraciones

**Solución:**
```bash
python manage.py migrate
```

### Problema: "Port 8000 already in use"

**Causa:** Ya tienes un servidor corriendo

**Solución:**
```bash
# Opción 1: Matar proceso
lsof -ti:8000 | xargs kill -9

# Opción 2: Usar otro puerto
python manage.py runserver 8001
```

### Problema: Pre-commit falla en commit

**Causa:** Código no cumple estándares

**Solución:**
```bash
# Ver qué falló
pre-commit run --all-files

# Formatear automáticamente
make format

# Intentar commit nuevamente
git add .
git commit -m "..."
```

### Problema: Tests fallan

**Causa:** Código roto o base de datos desincronizada

**Solución:**
```bash
# 1. Verificar que migraciones estén aplicadas
python manage.py migrate

# 2. Ejecutar tests con verbose para ver detalles
python manage.py test --verbosity=2

# 3. Si usas Docker, limpiar todo y empezar de nuevo
docker compose down -v
docker compose up -d
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py test
```

---

## Resumen: Tu Checklist Diario

### Al Empezar el Día

```bash
✓ source .venv/bin/activate
✓ git pull
✓ pip install -r requirements.txt -r requirements-dev.txt  # Solo si hay cambios
✓ python manage.py migrate  # Solo si hay cambios
✓ make run
```

### Mientras Desarrollas

```bash
✓ Cambios en models? → makemigrations → migrate
✓ Escribiste código? → make format
✓ Escribiste tests? → make test-app APP=nombre
```

### Antes de Commit

```bash
✓ make format
✓ make check
✓ make test
✓ git add . && git commit -m "..."
```

### Al Final del Día

```bash
✓ git push
✓ Ctrl+C (detener servidor)
✓ deactivate  # Desactivar entorno virtual
```

---

## Atajos de Cursor/VS Code

Si prefieres no usar la terminal, todas estas acciones están en Cursor Tasks:

- `Cmd+Shift+P` → "Tasks: Run Task"
- Selecciona la tarea que necesitas

**Las más usadas:**
- "Django: Run Server"
- "Django: Run All Tests"
- "Ruff: Format and Lint"
- "Django: Make Migrations"
- "Django: Migrate"

---

**¿Aún tienes dudas?** Consulta:
- [README.md](README.md) - Documentación general
- [DEVELOPMENT.md](DEVELOPMENT.md) - Guía completa de desarrollo
- `make help` - Ver todos los comandos disponibles
