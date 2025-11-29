# Guía Didáctica: Linting, Formatting y Pre-commit Hooks

## Tabla de Contenidos

1. [¿Qué Problema Resuelven Estas Herramientas?](#qué-problema-resuelven-estas-herramientas)
2. [Conceptos Fundamentales](#conceptos-fundamentales)
3. [Herramientas en Detalle](#herramientas-en-detalle)
4. [Flujo de Trabajo](#flujo-de-trabajo)
5. [Configuración](#configuración)
6. [Ventajas e Inconvenientes](#ventajas-e-inconvenientes)
7. [Casos de Uso Prácticos](#casos-de-uso-prácticos)
8. [Troubleshooting](#troubleshooting)
9. [Mejores Prácticas](#mejores-prácticas)
10. [Recursos Adicionales](#recursos-adicionales)

---

## ¿Qué Problema Resuelven Estas Herramientas?

### El Problema

Cuando múltiples desarrolladores trabajan en un proyecto, surgen problemas:

1. **Inconsistencia de Estilo**: Cada desarrollador tiene sus preferencias
   - Unos usan comillas simples, otros dobles
   - Diferentes estilos de indentación
   - Orden de imports variable

2. **Errores Comunes**: Bugs que se podrían detectar antes
   - Variables no utilizadas
   - Imports innecesarios
   - Código muerto
   - Problemas de seguridad básicos

3. **Code Reviews Improductivas**: Tiempo perdido discutiendo estilo
   - "Deberías usar comillas dobles"
   - "Los imports están desordenados"
   - "Hay espacios en blanco al final"

4. **Commits Problemáticos**: Código roto llega al repositorio
   - Tests que fallan
   - Sintaxis incorrecta
   - Secretos expuestos

### La Solución

**Automatizar** la verificación y corrección de código:

```
Desarrollador escribe código
         ↓
Herramientas automáticas verifican/corrigen
         ↓
Solo código correcto llega al repositorio
```

**Beneficios Inmediatos**:
- ✅ Código consistente sin esfuerzo manual
- ✅ Errores detectados antes de commit
- ✅ Code reviews enfocados en lógica, no estilo
- ✅ Onboarding más rápido de nuevos desarrolladores
- ✅ Menos bugs en producción

---

## Conceptos Fundamentales

### 1. Linting (Análisis Estático)

**¿Qué es?**

Un **linter** analiza código sin ejecutarlo para encontrar:
- Errores de sintaxis
- Problemas de estilo
- Bugs potenciales
- Malas prácticas
- Código no utilizado

**Analogía**: Como el corrector ortográfico de Word, pero para código.

**Ejemplo**:

```python
# Código con problemas
import os  # Import no usado
import sys

def calcular(x):
    y = x * 2  # Variable no usada
    return x + x

print("hola")  # print() en producción
```

**El linter detecta**:
- ⚠️ Import `os` no utilizado
- ⚠️ Variable `y` no utilizada
- ⚠️ `print()` statement (debería ser logging)

### 2. Formatting (Formateo)

**¿Qué es?**

Un **formatter** reescribe código para que siga un estilo consistente:
- Indentación uniforme
- Espacios alrededor de operadores
- Longitud de línea
- Orden de imports

**Analogía**: Como "Formatear párrafo" en Word.

**Ejemplo**:

```python
# ANTES - inconsistente
def foo(x,y, z):
    if x>0 and y<10:
      return x+y+z
    else:
           return 0

# DESPUÉS - formateado
def foo(x, y, z):
    if x > 0 and y < 10:
        return x + y + z
    else:
        return 0
```

### 3. Pre-commit Hooks

**¿Qué son?**

Scripts que se ejecutan **automáticamente** antes de cada commit:

```
Desarrollador hace: git commit
         ↓
Pre-commit hooks se ejecutan automáticamente
         ↓
¿Todo OK? → Commit procede
¿Errores? → Commit bloqueado, mostrar errores
```

**Analogía**: Como pasar por seguridad en el aeropuerto antes de abordar.

**Beneficios**:
- **Automático**: No necesitas recordar ejecutar comandos
- **Preventivo**: Bloquea commits problemáticos
- **Rápido**: Solo analiza archivos modificados

### 4. EditorConfig

**¿Qué es?**

Archivo de configuración (`.editorconfig`) que dice a TODOS los editores cómo formatear:

```ini
[*.py]
indent_size = 4
end_of_line = lf
charset = utf-8
```

**Beneficio**: Mismo formato en VS Code, PyCharm, Sublime, Vim, etc.

---

## Herramientas en Detalle

### Ruff: El Sustituto Moderno

#### ¿Qué es Ruff?

**Ruff** es un linter y formatter **ultra-rápido** escrito en Rust que **reemplaza**:

```
Black (formatter)
+ isort (ordenar imports)
+ flake8 (linter)
+ pylint (linter)
+ pyupgrade (modernizar código)
+ pydocstyle (docstrings)
+ bandit (seguridad)
= RUFF (todo en uno)
```

#### ¿Por qué Ruff?

**Velocidad**:
- 10-100x más rápido que herramientas tradicionales
- Analiza todo el proyecto en milisegundos

**Comparación**:
```
Proyecto de 100,000 líneas:
- Black + isort + flake8: ~45 segundos
- Ruff: ~1 segundo
```

**Unificado**:
- Una herramienta → más fácil de configurar
- Una configuración → más fácil de mantener

#### Reglas de Ruff

Ruff implementa **700+ reglas** agrupadas por categoría:

| Código | Herramienta Original | Descripción |
|--------|---------------------|-------------|
| E, W | pycodestyle | Errores y warnings de estilo PEP 8 |
| F | Pyflakes | Errores lógicos básicos |
| I | isort | Ordenamiento de imports |
| N | pep8-naming | Convenciones de nombres |
| UP | pyupgrade | Modernizar sintaxis Python |
| B | flake8-bugbear | Bugs comunes |
| DJ | flake8-django | Reglas específicas de Django |
| S | Bandit | Problemas de seguridad |
| C4 | flake8-comprehensions | List/dict comprehensions |
| SIM | flake8-simplify | Simplificaciones de código |

**Ejemplo de Reglas**:

```python
# E501: Línea demasiado larga (>100 caracteres)
def very_long_function_name_that_exceeds_the_maximum_line_length_limit_of_one_hundred_characters():
    pass

# F401: Import no utilizado
import os  # ← Ruff detecta que no se usa

# I001: Imports desordenados
import sys
import os  # ← Debería estar antes de sys

# B007: Variable no usada en loop
for i in range(10):  # ← 'i' no se usa
    print("hello")

# S105: Posible password hardcodeado
password = "admin123"  # ← Riesgo de seguridad

# DJ001: Model sin __str__
class User(models.Model):
    name = models.CharField()
    # ← Falta método __str__
```

#### Modos de Ruff

**1. Linter Mode** (solo detecta):
```bash
ruff check apps/
# Output:
# apps/users/models.py:10:1: F401 `os` imported but unused
# apps/users/views.py:25:80: E501 Line too long (102 > 100)
```

**2. Linter + Fix Mode** (detecta y arregla):
```bash
ruff check --fix apps/
# Arregla automáticamente:
# - Elimina imports no usados
# - Reordena imports
# - Simplifica código
```

**3. Formatter Mode** (reformatea):
```bash
ruff format apps/
# Reformatea:
# - Indentación
# - Espacios
# - Comillas
# - Longitud de línea
```

### Pre-commit Framework

#### ¿Cómo Funciona?

1. **Instalación**: `pre-commit install`
   - Crea un hook en `.git/hooks/pre-commit`

2. **Cuando haces commit**: `git commit -m "..."`
   - Git ejecuta automáticamente el hook
   - El hook ejecuta todas las verificaciones configuradas

3. **Resultado**:
   - ✅ **Éxito**: Commit procede normalmente
   - ❌ **Fallo**: Commit bloqueado, archivos modificados

#### Hooks Configurados

En `.pre-commit-config.yaml`:

```yaml
repos:
  # 1. Hooks básicos
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace      # Elimina espacios al final
      - id: end-of-file-fixer         # Agrega línea en blanco al final
      - id: check-yaml                # Valida YAML
      - id: check-json                # Valida JSON
      - id: mixed-line-ending         # Normaliza finales de línea

  # 2. Ruff
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff                      # Linter + fix
      - id: ruff-format               # Formatter

  # 3. Seguridad
  - repo: https://github.com/Yelp/detect-secrets
    hooks:
      - id: detect-secrets            # Detecta secretos/passwords

  # 4. Django
  - repo: https://github.com/adamchainz/django-upgrade
    hooks:
      - id: django-upgrade            # Moderniza código Django
```

#### Ejecución de Hooks

**Automática** (en cada commit):
```bash
git commit -m "feat: nueva funcionalidad"
# → Pre-commit se ejecuta automáticamente
# → Si pasa: commit procede
# → Si falla: commit bloqueado
```

**Manual** (cuando quieras):
```bash
# En todos los archivos
pre-commit run --all-files

# Solo en archivos staged
pre-commit run

# Un hook específico
pre-commit run ruff
```

### EditorConfig

#### Propósito

Asegurar que **todos los editores** usen las mismas configuraciones básicas.

#### Configuración (`.editorconfig`)

```ini
root = true

# Todos los archivos
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# Python
[*.py]
indent_style = space
indent_size = 4
max_line_length = 100

# JSON, YAML
[*.{json,yml,yaml}]
indent_size = 2
```

#### Soporte

Compatible con:
- VS Code (extensión EditorConfig)
- PyCharm (soporte nativo)
- Sublime Text (plugin)
- Vim/Neovim (plugin)
- Y más...

---

## Flujo de Trabajo

### Workflow Diario

```
┌─────────────────────────────────────────────────────────┐
│ 1. ESCRIBIR CÓDIGO                                      │
│    - Desarrollas normalmente en tu editor               │
│    - El editor respeta .editorconfig automáticamente    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. FORMATEAR (Opcional, pero recomendado)              │
│    make format                                           │
│    - Ruff formatea código automáticamente               │
│    - Ordena imports                                      │
│    - Arregla problemas simples                          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. VERIFICAR (Opcional)                                 │
│    make check                                            │
│    - Verifica sin modificar archivos                    │
│    - Muestra errores que debes corregir manualmente     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. HACER COMMIT                                         │
│    git add .                                             │
│    git commit -m "feat: nueva funcionalidad"            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 5. PRE-COMMIT HOOKS (Automático)                       │
│    - Trailing whitespace                                │
│    - End of file fixer                                  │
│    - Ruff linter                                        │
│    - Ruff formatter                                     │
│    - Detect secrets                                     │
│    - Django upgrade                                     │
└────────────────────────┬────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │         │
                  ✅         ❌
                    │         │
                    ↓         ↓
        ┌──────────────┐  ┌──────────────┐
        │ COMMIT OK    │  │ COMMIT       │
        │              │  │ BLOQUEADO    │
        │ Push cuando  │  │              │
        │ quieras      │  │ Revisar y    │
        │              │  │ corregir     │
        └──────────────┘  └──────────────┘
```

### Ejemplo Práctico Paso a Paso

#### Escenario: Agregar una nueva función

**Paso 1: Escribir código**

```python
# apps/users/services.py
import os  # Olvidaste que no lo usas
from apps.users.models import User


def get_user(user_id):  # Tipo hints faltantes
  user=User.objects.get(id=user_id)  # Mal formateado
  return user
```

**Paso 2: Formatear**

```bash
make format
# o
ruff format apps/ && ruff check --fix apps/
```

**Resultado automático**:

```python
# apps/users/services.py
from apps.users.models import User  # Import de 'os' eliminado


def get_user(user_id):  # Aún falta tipo hints
    user = User.objects.get(id=user_id)  # Formateado
    return user
```

**Paso 3: Verificar**

```bash
make check
# o
ruff check apps/
```

**Output**:
```
apps/users/services.py:4:1: ANN001 Missing type annotation for function argument `user_id`
apps/users/services.py:4:1: ANN201 Missing return type annotation for public function
```

**Corriges manualmente**:

```python
# apps/users/services.py
from apps.users.models import User


def get_user(user_id: int) -> User:  # Agregado tipo hints
    user = User.objects.get(id=user_id)
    return user
```

**Paso 4: Commit**

```bash
git add apps/users/services.py
git commit -m "feat(users): agregar función get_user"
```

**Pre-commit hooks se ejecutan**:

```
Trim Trailing Whitespace.................................................Passed
Fix End of Files.........................................................Passed
Check Yaml...............................................................Passed
Check JSON...............................................................Passed
Check Toml...............................................................Passed
Check for added large files..............................................Passed
Check for merge conflicts................................................Passed
Mixed line ending........................................................Passed
Debug Statements (Python)................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
detect-secrets...........................................................Passed
django-upgrade...........................................................Passed
```

✅ **Commit exitoso!**

#### Si hubiera un error:

```bash
git commit -m "feat: algo"
```

**Output**:
```
ruff.....................................................................Failed
- hook id: ruff
- exit code: 1

apps/users/views.py:15:1: F401 [*] `os` imported but unused
apps/users/views.py:20:5: S105 Possible hardcoded password: "admin123"

2 errors found
```

❌ **Commit bloqueado**

**Acciones**:
1. Revisar errores
2. Corregir manualmente o con `ruff check --fix`
3. Hacer `git add` nuevamente
4. Intentar commit otra vez

---

## Configuración

### Archivos de Configuración

#### 1. `pyproject.toml` - Configuración de Ruff

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "I",      # isort
    "DJ",     # flake8-django
]

ignore = [
    "E501",   # Longitud de línea (ya controlado por line-length)
]

[tool.ruff.lint.per-file-ignores]
# Ignorar reglas específicas en tests
"**/tests.py" = ["S101"]  # Permite assert en tests
```

**Personalización Común**:

```toml
# Cambiar longitud de línea
line-length = 120  # Default: 88 (Black), proyecto usa 100

# Agregar/quitar reglas
select = ["ALL"]  # Activar todas
ignore = ["D"]    # Desactivar docstring checks

# Por archivo
"migrations/*.py" = ["ALL"]  # No lint migrations
```

#### 2. `.pre-commit-config.yaml` - Configuración de Hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9  # Versión
    hooks:
      - id: ruff
        args: [--fix]  # Argumentos adicionales
```

**Personalización Común**:

```yaml
# Actualizar versiones
pre-commit autoupdate

# Saltarse un hook temporalmente
SKIP=ruff git commit -m "WIP"

# Desactivar un hook
# - id: ruff
#   skip: true
```

#### 3. `.editorconfig` - Configuración de Editor

```ini
[*.py]
indent_size = 4
max_line_length = 100
```

**Personalización Común**:

```ini
# TypeScript/JavaScript
[*.{ts,js}]
indent_size = 2

# Markdown (no trim whitespace)
[*.md]
trim_trailing_whitespace = false
```

### Instalación en Nuevo Proyecto

```bash
# 1. Crear archivos de configuración
# Copiar: pyproject.toml, .pre-commit-config.yaml, .editorconfig

# 2. Instalar dependencias
pip install ruff pre-commit

# 3. Instalar hooks
pre-commit install

# 4. Ejecutar en todo el código existente
ruff format .
ruff check --fix .
pre-commit run --all-files

# 5. Commit de configuración
git add .
git commit -m "chore: configurar linting y pre-commit"
```

---

## Ventajas e Inconvenientes

### Ventajas ✅

#### 1. Consistencia Automática

**Sin herramientas**:
```python
# Archivo A
def foo( x,y ):
    return x+y

# Archivo B
def bar(x, y):
    return x + y
```

**Con herramientas**:
```python
# Ambos archivos formateados igual
def foo(x, y):
    return x + y

def bar(x, y):
    return x + y
```

#### 2. Detección Temprana de Errores

```python
# Este código "funciona" pero tiene bugs potenciales
def process_data(data):
    import json  # ← Import en función (ineficiente)
    result = []
    for item in data:
        x = item['value']  # ← Puede fallar si 'value' no existe
        result.append(x * 2)
    unused_var = 10  # ← Variable no usada
    return result
```

**Ruff detecta**:
- Import en función (mejor arriba)
- Falta manejo de KeyError
- Variable no usada

#### 3. Code Reviews más Eficientes

**Sin herramientas** (50% del review):
> - ❌ Usa comillas dobles
> - ❌ Ordena los imports
> - ❌ Elimina espacios en blanco
> - ❌ Agrega type hints
> - ✅ Lógica correcta

**Con herramientas** (100% en lógica):
> - ✅ Estilo: Automático ✓
> - ✅ Lógica correcta
> - 💬 Sugerencia: ¿Considerar usar cache aquí?

#### 4. Onboarding Rápido

Nuevo desarrollador:
```bash
git clone ...
pip install -r requirements-dev.txt
pre-commit install

# ¡Listo! No necesita aprender convenciones manualmente
```

#### 5. Velocidad (Especialmente Ruff)

```
Proyecto 50,000 líneas:

Black + isort + flake8: ~25 segundos
Ruff: ~0.5 segundos

50x más rápido = feedback instantáneo
```

### Inconvenientes ❌

#### 1. Curva de Aprendizaje Inicial

**Tiempo de setup**: 30-60 minutos primera vez
- Entender herramientas
- Configurar archivos
- Ajustar a preferencias del equipo

**Mitigación**: Usar configuración estándar, personalizar después.

#### 2. Configuración Inicial Puede Ser Abrumadora

`pyproject.toml` puede tener 100+ líneas de configuración.

**Mitigación**:
- Empezar con configuración mínima
- Agregar reglas gradualmente
- Copiar configuración de proyectos similares

#### 3. Commits Bloqueados (Puede Ser Frustrante)

```bash
git commit -m "WIP"
# ❌ Pre-commit falla por errores de estilo
# Frustración: "¡Solo quiero guardar mi progreso!"
```

**Mitigación**:
```bash
# Saltarse hooks temporalmente (usar con precaución)
git commit --no-verify -m "WIP"

# O hacer commit de archivos individuales
git commit file.py -m "WIP"  # Solo este archivo
```

#### 4. False Positives

A veces el linter se queja de algo intencional:

```python
# Linter: "Variable no usada"
_ = expensive_calculation()  # Intencional: ejecutar por efecto secundario

# Solución: Ignorar en esa línea
_ = expensive_calculation()  # noqa: F841
```

#### 5. Conflictos en Merge

Si dos ramas formatean diferente:

```
Branch A: formateado con Black
Branch B: formateado con Ruff
Merge: Conflictos de estilo
```

**Mitigación**:
- Equipo adopta herramientas al mismo tiempo
- Formatear todo el código en un commit inicial
- Usar `.git-blame-ignore-revs` para ignorar commits de formatting

#### 6. Dependencia de Herramientas Externas

Si Ruff o pre-commit tienen bugs:
- Puede bloquear desarrollo
- Requiere actualizar/downgrade

**Mitigación**:
- Fijar versiones en configuración
- Tener plan de rollback
- Mantener herramientas actualizadas

### Tabla Comparativa

| Aspecto | Sin Herramientas | Con Herramientas |
|---------|------------------|------------------|
| **Consistencia de estilo** | Manual, inconsistente | Automática, 100% |
| **Detección de errores** | En runtime o reviews | Antes de commit |
| **Tiempo de code review** | 50% estilo, 50% lógica | 100% lógica |
| **Setup inicial** | 0 min | 30-60 min |
| **Tiempo diario extra** | 0 min (pero más bugs) | ~1-2 min |
| **Frustración inicial** | Baja | Media-Alta |
| **Frustración a largo plazo** | Alta (deuda técnica) | Baja |
| **Bugs en producción** | Más | Menos |
| **Velocidad de feedback** | Lenta (manual) | Instantánea |

---

## Casos de Uso Prácticos

### Caso 1: Proyecto Nuevo

**Situación**: Empiezas un proyecto desde cero.

**Estrategia**:

```bash
# 1. Crear estructura
mkdir my-project && cd my-project
git init

# 2. Agregar configuración (copiar archivos)
# - pyproject.toml
# - .pre-commit-config.yaml
# - .editorconfig

# 3. Instalar herramientas
pip install ruff pre-commit
pre-commit install

# 4. Empezar a desarrollar
# ✅ Todo el código futuro será consistente desde el principio
```

**Ventaja**: No hay código legacy que reformatear.

### Caso 2: Proyecto Existente (Legacy)

**Situación**: Proyecto de 50,000 líneas sin formatear.

**Estrategia Gradual**:

```bash
# Opción A: Big Bang (todo de una vez)
ruff format .
ruff check --fix .
git add .
git commit -m "chore: formatear todo el código base"
# + Agregar a .git-blame-ignore-revs

# Opción B: Gradual (por directorio)
ruff format apps/users/
git commit -m "chore: formatear app users"
# Repetir para cada app

# Opción C: Solo archivos nuevos/modificados
# Configurar pre-commit para solo actuar en staged files (default)
```

**Recomendación**: Opción A (Big Bang) + `.git-blame-ignore-revs`

```bash
# .git-blame-ignore-revs
# Commit de formateo masivo
abc123def456789
```

```bash
# Configurar git para ignorar ese commit en blame
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

### Caso 3: Equipo Distribuido

**Situación**: 5 desarrolladores, diferentes editores, diferentes OS.

**Problema**: Inconsistencias de:
- Finales de línea (CRLF vs LF)
- Indentación (tabs vs espacios)
- Encoding (UTF-8 vs Latin-1)

**Solución**:

```ini
# .editorconfig
root = true

[*]
end_of_line = lf        # Unix line endings
charset = utf-8         # UTF-8 siempre
indent_style = space    # Espacios, no tabs
```

```toml
# pyproject.toml
[tool.ruff.format]
line-ending = "lf"
```

**Resultado**: Mismo formato en Windows, Mac, Linux.

### Caso 4: CI/CD Pipeline

**Situación**: Quieres verificar en CI antes de mergear.

**GitHub Actions** (`.github/workflows/lint.yml`):

```yaml
name: Lint

on: [pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install Ruff
        run: pip install ruff
      
      - name: Run Ruff
        run: |
          ruff check .
          ruff format --check .
```

**Resultado**: PRs bloqueados si código no cumple estándares.

### Caso 5: Migración de Herramientas

**Situación**: Proyecto usa Black + isort + flake8, quieres migrar a Ruff.

**Plan de Migración**:

```bash
# 1. Instalar Ruff
pip install ruff

# 2. Configurar equivalente en pyproject.toml
[tool.ruff]
line-length = 88  # Mismo que Black
[tool.ruff.lint]
select = ["E", "F", "I"]  # Equivalente a flake8 + isort

# 3. Formatear con Ruff
ruff format .

# 4. Verificar que da mismos resultados
diff <(black --check .) <(ruff format --check .)

# 5. Si OK, desinstalar herramientas viejas
pip uninstall black isort flake8

# 6. Actualizar .pre-commit-config.yaml
# Reemplazar hooks de Black/isort/flake8 con Ruff

# 7. Commit
git commit -m "chore: migrar de Black/flake8 a Ruff"
```

---

## Troubleshooting

### Problema 1: Pre-commit Hooks No Se Ejecutan

**Síntomas**:
```bash
git commit -m "test"
# No output de pre-commit
```

**Causa**: Hooks no instalados.

**Solución**:
```bash
pre-commit install
# Output: pre-commit installed at .git/hooks/pre-commit
```

### Problema 2: Hooks Fallan por Errores de Instalación

**Síntomas**:
```
[ERROR] An unexpected error has occurred: CalledProcessError: ...
```

**Solución**:
```bash
# Limpiar y reinstalar
pre-commit clean
pre-commit install --install-hooks
pre-commit run --all-files
```

### Problema 3: Ruff Encuentra Demasiados Errores

**Síntomas**:
```
Found 500 errors
```

**Solución Gradual**:

```toml
# pyproject.toml - Empezar con reglas mínimas
[tool.ruff.lint]
select = ["E", "F"]  # Solo lo esencial

# Luego agregar gradualmente
select = ["E", "F", "I"]  # + imports
select = ["E", "F", "I", "N"]  # + naming
# ...
```

### Problema 4: Conflictos con Configuración del Editor

**Síntomas**: Editor formatea diferente que Ruff.

**Solución**:

```json
// VS Code: settings.json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"  // Usar Ruff
  }
}
```

**PyCharm**: Settings → Tools → External Tools → Configurar Ruff

### Problema 5: Línea Demasiado Larga pero Inevitable

**Síntomas**:
```python
# Ruff: E501 Line too long (150 > 100)
very_long_url = "https://api.example.com/v1/users?filter=active&sort=created&limit=100&offset=0"
```

**Solución**:

```python
# Opción 1: Ignorar en esa línea
very_long_url = "https://..."  # noqa: E501

# Opción 2: Reformatear
very_long_url = (
    "https://api.example.com/v1/users"
    "?filter=active&sort=created&limit=100&offset=0"
)

# Opción 3: Aumentar límite para URLs
[tool.ruff.lint.per-file-ignores]
"**/urls.py" = ["E501"]
```

### Problema 6: Pre-commit Muy Lento

**Síntomas**: Commits tardan 30+ segundos.

**Causa**: Hooks ejecutan en todos los archivos.

**Solución**:

```yaml
# .pre-commit-config.yaml
- id: ruff
  stages: [commit]  # Solo en commit, no en push
  pass_filenames: true  # Solo archivos modificados (default)
```

```bash
# Si sigue lento, desactivar hooks innecesarios
SKIP=detect-secrets git commit -m "..."
```

---

## Mejores Prácticas

### 1. Empezar Simple, Crecer Gradualmente

**❌ No hagas esto**:
```toml
select = ["ALL"]  # Todas las 700+ reglas
```

**✅ Haz esto**:
```toml
# Semana 1
select = ["E", "F"]  # Esencial

# Semana 2
select = ["E", "F", "I"]  # + imports

# Semana 3
select = ["E", "F", "I", "N", "UP"]  # + naming + modernización
```

### 2. Formatear Todo al Inicio

Si adoptas en proyecto existente:

```bash
# 1. Formatear todo
ruff format .
ruff check --fix .

# 2. Commit separado
git commit -m "chore: formatear código base con Ruff"

# 3. Agregar a ignore-revs
echo $(git rev-parse HEAD) >> .git-blame-ignore-revs
```

### 3. Documentar Excepciones

Cuando ignoras una regla:

```python
# ❌ No hagas esto
password = "admin123"  # noqa

# ✅ Haz esto
password = "admin123"  # noqa: S105 - Password de testing, no producción
```

### 4. Configurar CI/CD

Siempre verificar en CI:

```yaml
# .github/workflows/ci.yml
- name: Lint
  run: |
    pip install ruff
    ruff check .
    ruff format --check .
```

### 5. Hacer Commits Frecuentes

```bash
# ✅ Bueno
git add feature.py
git commit -m "feat: agregar función X"
# Pre-commit verifica solo feature.py

# ❌ Malo
git add .
git commit -m "feat: muchos cambios"
# Pre-commit verifica 50 archivos, tarda más
```

### 6. Usar Makefile para Comandos

```makefile
.PHONY: format check lint

format:
	ruff format .
	ruff check --fix .

check:
	ruff check .
	ruff format --check .

lint:
	ruff check .
```

```bash
# Comandos simples
make format
make check
```

### 7. Educar al Equipo

**No asumas que todos entienden**:

```markdown
# docs/CONTRIBUTING.md

## Antes de tu primer commit

1. Instalar herramientas: `pip install -r requirements-dev.txt`
2. Instalar hooks: `pre-commit install`
3. Formatear código: `make format`
4. Verificar: `make check`
5. Commit: `git commit -m "..."`

Si el commit falla:
- Revisar errores mostrados
- Corregir manualmente o con `make format`
- Intentar nuevamente
```

### 8. Revisar Configuración Periódicamente

```bash
# Cada 3-6 meses
# 1. Actualizar herramientas
pre-commit autoupdate
pip install --upgrade ruff

# 2. Revisar nuevas reglas de Ruff
ruff linter

# 3. Considerar agregar nuevas reglas útiles
```

### 9. No Pelear con las Herramientas

Si Ruff formatea de cierta manera:

**❌ No hagas esto**:
```python
# fmt: off
my_list = [1,2,3,4,5]
# fmt: on
```

**✅ Acepta el formato** (probablemente hay una razón):
```python
my_list = [1, 2, 3, 4, 5]
```

### 10. Monitorear Métricas

Track mejoras:

```bash
# Antes de adoptar
ruff check . | wc -l
# 500 errores

# 3 meses después
ruff check . | wc -l
# 50 errores

# 6 meses después
ruff check . | wc -l
# 5 errores
```

---

## Recursos Adicionales

### Documentación Oficial

- **Ruff**: https://docs.astral.sh/ruff/
  - Tutorial: https://docs.astral.sh/ruff/tutorial/
  - Reglas: https://docs.astral.sh/ruff/rules/
  - Configuration: https://docs.astral.sh/ruff/configuration/

- **Pre-commit**: https://pre-commit.com/
  - Hooks disponibles: https://pre-commit.com/hooks.html
  - Writing hooks: https://pre-commit.com/#creating-new-hooks

- **EditorConfig**: https://editorconfig.org/

### Guías de Estilo Python

- **PEP 8**: https://peps.python.org/pep-0008/
  - Guía oficial de estilo Python

- **Google Python Style Guide**: https://google.github.io/styleguide/pyguide.html

- **Django Coding Style**: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/

### Comparaciones y Benchmarks

- **Ruff vs Black vs flake8**: https://github.com/astral-sh/ruff#how-does-ruff-compare-to-flake8-black-isort-and-pylint

### Plugins de Editores

**VS Code**:
- Ruff: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff
- EditorConfig: https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig

**PyCharm**:
- Ruff: https://plugins.jetbrains.com/plugin/20574-ruff
- EditorConfig: Soporte nativo

### Comunidad

- **Ruff GitHub**: https://github.com/astral-sh/ruff
- **Pre-commit GitHub**: https://github.com/pre-commit/pre-commit

---

## Conclusión

### Resumen de Conceptos Clave

1. **Linting**: Detecta errores sin ejecutar código
2. **Formatting**: Reformatea código automáticamente
3. **Pre-commit**: Ejecuta checks automáticamente antes de commit
4. **Ruff**: Herramienta moderna que unifica todo (10-100x más rápido)
5. **EditorConfig**: Asegura consistencia entre editores

### Cuándo Adoptar Estas Herramientas

✅ **Adopta SI**:
- Equipo de 2+ desarrolladores
- Proyecto de larga duración (6+ meses)
- Código que cambia frecuentemente
- Quieres reducir bugs
- Code reviews tardan mucho en estilo

❌ **No urgente SI**:
- Proyecto personal de 1 semana
- Script de una sola vez
- Prototipo rápido que se va a tirar

### Checklist de Adopción

- [ ] Instalar herramientas: `pip install ruff pre-commit`
- [ ] Crear/copiar archivos de configuración
- [ ] Formatear código base existente: `ruff format . && ruff check --fix .`
- [ ] Instalar hooks: `pre-commit install`
- [ ] Probar: `pre-commit run --all-files`
- [ ] Documentar en README/CONTRIBUTING.md
- [ ] Educar al equipo
- [ ] Configurar CI/CD
- [ ] Hacer commit inicial: `git commit -m "chore: configurar linting"`

### Siguiente Paso

```bash
# En tu proyecto
cd /path/to/project

# Instalar
pip install ruff pre-commit

# Ejecutar
ruff format .
ruff check --fix .

# Ver resultados
git diff
```

¡Disfruta de código más limpio y consistente! 🎉

---

**Última actualización**: 2025-11-29  
**Versión**: 1.0  
**Autor**: Equipo de The Natural Way
