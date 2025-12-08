# Quality Reports

Este directorio contiene todos los reportes de calidad del código generados automáticamente.

## 📁 Estructura

```
docs/quality-reports/
├── README.md                    # Este archivo
├── coverage/                    # Reportes de cobertura de tests
│   ├── index.html              # 🌐 Dashboard principal de coverage
│   └── ...                     # Archivos HTML detallados por módulo
├── code-analysis/              # Reportes JSON (fuente de datos)
│   ├── ruff.json               # Problemas de estilo y bugs
│   ├── complexity.json         # Complejidad ciclomática
│   ├── maintainability.json    # Índice de mantenibilidad
│   ├── security.json           # Vulnerabilidades de seguridad
│   ├── mypy.txt                # Type checking estático
│   └── dead-code.txt           # Código muerto/no usado
└── YYYYMMDD-code-analysis/     # Dashboards HTML por fecha
    └── dashboard.html          # 🌐 Dashboard de calidad (ej: 20251208-code-analysis/)
```

**Nota**: Los dashboards HTML se guardan en carpetas con formato `YYYYMMDD-code-analysis`.
Si generas el dashboard varias veces el mismo día, se reescribe en la misma carpeta.

## 🚀 Generar Reportes

### Coverage (Cobertura de Tests)

```bash
# Generar reporte de coverage + abrir dashboard
make coverage
```

### Code Analysis (Análisis de Calidad)

#### Opción 1: Resumen Rápido (Recomendado para desarrollo diario)
```bash
# Resumen rápido en terminal (~5s, no genera archivos)
make quality-summary
```

#### Opción 2: Análisis Completo + Dashboard (Recomendado para PR)
```bash
# Análisis completo + dashboard HTML en un solo comando (~15s)
make quality-dashboard
```

#### Opción 3: Paso a Paso (Avanzado)
```bash
# 1. Generar reportes JSON
make quality

# 2. Generar dashboard HTML desde JSON existentes
make quality-html
```

## 🌐 Dashboards HTML

### Coverage Dashboard
- **URL**: `docs/quality-reports/coverage/index.html`
- **Muestra**: Cobertura de tests por archivo y línea
- **Actualizar**: `make coverage`

### Code Quality Dashboard
- **URL**: `docs/quality-reports/YYYYMMDD-code-analysis/dashboard.html` (donde YYYYMMDD es la fecha de hoy)
- **Ejemplo**: `docs/quality-reports/20251208-code-analysis/dashboard.html`
- **Actualizar**: `make quality-dashboard` (todo en uno) o `make quality-html` (solo dashboard)
- **Nota**: Cada día se crea una nueva carpeta. Si regeneras el dashboard el mismo día, se reescribe.

#### 🎨 Características del Dashboard

**Navegación:**
- 📄 Menú lateral fijo con 7 secciones
- 🎯 Navegación suave al hacer click
- ✨ Auto-detección de sección activa al scrollear
- 🔽 Secciones colapsables con animaciones

**Contenido:**
- 📄 **Overview del Proyecto**: Stack tecnológico, descripción, arquitectura
- 🔄 **Complejidad Ciclomática**: Promedio + distribución A-F + top 30 funciones complejas
- 🔧 **Índice de Mantenibilidad**: Score 0-100 + distribución A-C + archivos problemáticos
- 🔵 **Mypy Type Checker**: Total errores de tipos + top 5 tipos de error + detalles
- ⚡ **Ruff Linter**: Total problemas + errores vs warnings + tabla de detalles
- 🔒 **Seguridad**: Distribución HIGH/MEDIUM/LOW + top 15 vulnerabilidades
- 💀 **Código Muerto**: Total items + top 30 funciones/variables no usadas

**Diseño:**
- ✅ Explicaciones en español de cada métrica
- 📊 Valores óptimos/warning/críticos claramente indicados
- 📑 Tablas interactivas con detalles accionables
- 🎨 Diseño profesional y responsive
- 🔵 Indicadores visuales con colores (verde/amarillo/rojo)

## 📊 Reportes JSON

Los archivos JSON contienen datos detallados que puede ser procesados:

- `ruff.json` - Lista de problemas detectados por Ruff (linting, estilo)
- `complexity.json` - Complejidad de cada función
- `maintainability.json` - Índice de mantenibilidad por archivo
- `security.json` - Vulnerabilidades detectadas con detalles
- `mypy.txt` - Errores de type checking (tipos estáticos)
- `dead-code.txt` - Código no utilizado

## 🔄 Actualización

Los reportes NO se commitean al repositorio (están en `.gitignore`).

Cada desarrollador debe generar sus propios reportes localmente:

```bash
# Coverage
make coverage

# Análisis de calidad (recomendado)
make quality-dashboard
```

## ⏱️ Frecuencia Recomendada

| Cuándo | Comando | Duración | Salida |
|--------|---------|----------|--------|
| **Desarrollo diario** | `make quality-summary` | ~5s | Terminal |
| **Antes de commit** | `make quality-summary` | ~5s | Terminal |
| **Antes de PR** | `make quality-dashboard` | ~15s | Dashboard HTML |
| **Revisión semanal** | `make quality-dashboard` | ~15s | Dashboard HTML |
| **Coverage** | `make coverage` | ~10s | Dashboard HTML |

### 💡 Comandos Disponibles

```bash
# 1. Resumen rápido (solo terminal, sin archivos)
make quality-summary

# 2. Análisis completo (genera JSON)
make quality

# 3. Dashboard HTML (requiere JSON previos)
make quality-html

# 4. TODO EN UNO: análisis + dashboard (recomendado)
make quality-dashboard
```

## 🎯 Métricas Objetivo

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Test Coverage | > 80% | Ver coverage dashboard |
| Complejidad Promedio | < 10 | Ver quality dashboard |
| Mantenibilidad | > 20 (A) | Ver quality dashboard |
| Pylint Score | > 8.0 | Ver quality dashboard |
| Vulnerabilidades HIGH | 0 | Ver quality dashboard |

## 👨‍💻 Comandos de Cursor/VS Code

Todas estas tareas están disponibles en Cursor/VS Code:

**Cmd+Shift+P** → "Tasks: Run Task" → Seleccionar:

- **Quality: Quick Summary (Terminal)** - Resumen rápido
- **Quality: Full Analysis** - Genera solo JSON
- **Quality: Generate HTML Dashboard** - Genera solo dashboard
- **Quality: Full Analysis + Dashboard** - Todo en uno ⭐

## 📊 Workflow Recomendado

### Durante Desarrollo
```bash
# Check rápido cada hora o antes de commit
make quality-summary
```

### Antes de Pull Request
```bash
# Análisis completo + dashboard visual
make quality-dashboard

# Revisar dashboard en navegador
# Se abre automáticamente
```

### Revisión Semanal
```bash
# Coverage + Quality completo
make coverage
make quality-dashboard

# Revisar tendencias y métricas objetivo
```

## 📖 Más Información

- [CODE_QUALITY_ANALYSIS.md](../CODE_QUALITY_ANALYSIS.md) - Guía completa de análisis de calidad
- [LINTING_AND_PRECOMMIT_GUIDE.md](../LINTING_AND_PRECOMMIT_GUIDE.md) - Guía de linting y pre-commit
- [Makefile](../../Makefile) - Ver todos los comandos con `make help`
