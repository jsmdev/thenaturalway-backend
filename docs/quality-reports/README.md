# Quality Reports

Este directorio contiene todos los reportes de calidad del código generados automáticamente.

## 📁 Estructura

```
docs/quality-reports/
├── README.md                    # Este archivo
├── coverage/                    # Reportes de cobertura de tests
│   ├── index.html              # 🌐 Dashboard principal de coverage
│   └── ...                     # Archivos HTML detallados por módulo
└── code-analysis/              # Análisis de calidad de código
    ├── dashboard.html          # 🌐 Dashboard principal de calidad
    ├── ruff.json               # Problemas de estilo y bugs
    ├── complexity.json         # Complejidad ciclomática
    ├── maintainability.json    # Índice de mantenibilidad
    ├── security.json           # Vulnerabilidades de seguridad
    ├── pylint.json             # Linting exhaustivo
    └── dead-code.txt           # Código muerto/no usado
```

## 🚀 Generar Reportes

### Coverage (Cobertura de Tests)

```bash
# Generar reporte de coverage
make coverage

# Ver dashboard
open docs/quality-reports/coverage/index.html
```

### Code Analysis (Análisis de Calidad)

```bash
# Generar reportes JSON
make quality

# Generar dashboard HTML
make quality-html

# Ver dashboard
open docs/quality-reports/code-analysis/dashboard.html
```

## 🌐 Dashboards HTML

### Coverage Dashboard
- **URL**: `docs/quality-reports/coverage/index.html`
- **Muestra**: Cobertura de tests por archivo y línea
- **Actualizar**: `make coverage`

### Code Quality Dashboard
- **URL**: `docs/quality-reports/code-analysis/dashboard.html`
- **Muestra**:
  - Complejidad ciclomática
  - Índice de mantenibilidad
  - Pylint score
  - Vulnerabilidades de seguridad (top 10)
- **Actualizar**: `make quality && make quality-html`

## 📊 Reportes JSON

Los archivos JSON contienen datos detallados que puede ser procesados:

- `ruff.json` - Lista de problemas detectados por Ruff
- `complexity.json` - Complejidad de cada función
- `maintainability.json` - Índice de mantenibilidad por archivo
- `security.json` - Vulnerabilidades detectadas con detalles
- `pylint.json` - Análisis exhaustivo de Pylint
- `dead-code.txt` - Código no utilizado

## 🔄 Actualización

Los reportes NO se commitean al repositorio (están en `.gitignore`).

Cada desarrollador debe generar sus propios reportes localmente:

```bash
# Generar todos los reportes
make coverage
make quality
make quality-html
```

## ⏱️ Frecuencia Recomendada

- **Coverage**: Después de escribir/modificar tests
- **Code Analysis**: 
  - Antes de cada commit: `make quality-summary` (rápido)
  - Antes de PR: `make quality && make quality-html` (completo)
  - Semanal: Revisar tendencias en los dashboards

## 🎯 Métricas Objetivo

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Test Coverage | > 80% | Ver coverage dashboard |
| Complejidad Promedio | < 10 | Ver quality dashboard |
| Mantenibilidad | > 20 (A) | Ver quality dashboard |
| Pylint Score | > 8.0 | Ver quality dashboard |
| Vulnerabilidades HIGH | 0 | Ver quality dashboard |

## 📖 Más Información

- [CODE_QUALITY_ANALYSIS.md](../CODE_QUALITY_ANALYSIS.md) - Guía completa de análisis de calidad
- [Makefile](../../Makefile) - Ver comandos disponibles con `make help`
