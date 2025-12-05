# Análisis de Calidad de Código - Guía Completa

## 📊 Overview

Este proyecto incluye un **sistema exhaustivo de análisis de calidad** que va más allá del linting básico, proporcionando métricas detalladas de complejidad, mantenibilidad, seguridad y código muerto.

## 🛠️ Herramientas Integradas

### 1. **Ruff** - Linter Ultra-Rápido
Ya configurado, detecta errores de estilo, bugs potenciales, y problemas de seguridad básicos.

### 2. **Radon** - Métricas de Complejidad
- **Complejidad Ciclomática**: Mide cuántos caminos independientes hay en el código
- **Índice de Mantenibilidad**: Score de 0-100 sobre qué tan fácil es mantener el código
- **Métricas Raw**: LOC, SLOC, comentarios, blanks
- **Métricas de Halstead**: Volumen, dificultad, esfuerzo

### 3. **Bandit** - Análisis de Seguridad
Detecta vulnerabilidades comunes en Python:
- SQL injection
- Hardcoded passwords
- Uso inseguro de librerías
- Comandos shell inseguros
- Y más...

### 4. **Pylint** - Linting Exhaustivo
Análisis más profundo que Ruff:
- Convenciones de naming
- Uso de variables
- Imports circulares
- Diseño de clases
- Métricas adicionales

### 5. **Vulture** - Código Muerto
Encuentra código no utilizado:
- Funciones nunca llamadas
- Variables no usadas
- Imports innecesarios
- Clases sin instanciar

## 🚀 Uso Rápido

### Análisis Completo

**Desde terminal:**
```bash
make quality
```

**Desde Cursor:**
`Cmd+Shift+P` → "Tasks: Run Task" → **"Quality: Full Analysis"**

Genera reportes JSON en `quality-reports/`:
- `ruff.json` - Problemas de estilo y bugs
- `complexity.json` - Complejidad ciclomática
- `maintainability.json` - Índice de mantenibilidad
- `security.json` - Vulnerabilidades de seguridad
- `pylint.json` - Linting exhaustivo
- `dead-code.txt` - Código muerto/no usado

### Resumen Rápido (Terminal)

```bash
make quality-summary
```

**Desde Cursor:**
`Cmd+Shift+P` → "Tasks: Run Task" → **"Quality: Summary"**

Muestra resumen en terminal sin generar archivos.

## 📋 Comandos Individuales

### Complejidad Ciclomática

**Terminal:**
```bash
radon cc apps/ -a -s
```

**Cursor Task:** "Quality: Complexity Analysis"

**Interpretar resultados:**
- **A (1-5)**: Simple, fácil de entender
- **B (6-10)**: Bastante simple
- **C (11-20)**: Complejidad moderada
- **D (21-30)**: Más complejo, considerar refactorizar
- **E (31-40)**: Muy complejo, refactorizar
- **F (41+)**: Extremadamente complejo, urgente refactorizar

### Índice de Mantenibilidad

**Terminal:**
```bash
radon mi apps/ -s
```

**Cursor Task:** "Quality: Maintainability Index"

**Interpretar resultados:**
- **A (100-20)**: Muy mantenible
- **B (19-10)**: Moderadamente mantenible
- **C (9-0)**: Difícil de mantener

### Análisis de Seguridad

**Terminal:**
```bash
bandit -r apps/ -ll  # Solo high/medium severity
bandit -r apps/      # Todos los niveles
```

**Cursor Task:** "Quality: Security Scan"

**Interpretar resultados:**
- **HIGH**: Vulnerabilidad seria, arreglar inmediatamente
- **MEDIUM**: Problema potencial, revisar
- **LOW**: Mejora recomendada

### Código Muerto

**Terminal:**
```bash
vulture apps/ --min-confidence 80
```

**Cursor Task:** "Quality: Dead Code Detection"

**Interpretar resultados:**
- **Confidence 100%**: Definitivamente no usado
- **Confidence 80-99%**: Muy probable que no se use
- **Confidence 60-79%**: Revisar manualmente

### Pylint Exhaustivo

**Terminal:**
```bash
pylint apps/
```

**Cursor Task:** "Quality: Pylint Full"

**Interpretar resultados:**
Score de 0-10. Ideal: > 8.0

## 📊 Ejemplo de Workflow

### 1. Antes de Hacer Commit

```bash
# Quick check
make quality-summary
```

Si ves problemas serios → arreglar → continuar

### 2. Antes de PR/Release

```bash
# Análisis completo
make quality

# Revisar reportes
ls quality-reports/
```

Revisar archivos JSON y asegurar que no hay:
- Complejidad F
- Vulnerabilidades HIGH
- Mantenibilidad C en archivos críticos

### 3. Análisis Periódico (Semanal/Mensual)

```bash
make quality
```

Comparar métricas con análisis anterior:
- ¿Aumentó la complejidad?
- ¿Hay más código muerto?
- ¿Bajó el índice de mantenibilidad?

## 🎯 Métricas Objetivo

### Por Archivo/Función

| Métrica | Bueno | Aceptable | Refactorizar |
|---------|-------|-----------|--------------|
| Complejidad Ciclomática | A (1-5) | B-C (6-20) | D-F (21+) |
| Mantenibilidad | A (20-100) | B (10-19) | C (0-9) |
| LOC por función | < 20 | 20-50 | > 50 |
| Seguridad | 0 issues | LOW only | MEDIUM/HIGH |

### Por Proyecto

| Métrica | Objetivo |
|---------|----------|
| Pylint Score | > 8.0 |
| Test Coverage | > 80% |
| Código Muerto | < 5% |
| Complejidad Promedio | < 10 |

## 🔧 Configuración Avanzada

### Radon

Crear `.radon.cfg`:
```ini
[radon]
exclude = */migrations/*,*/tests.py
average = True
total_average = True
```

### Bandit

Crear `.bandit`:
```yaml
exclude_dirs:
  - /tests/
  - /migrations/

skips:
  - B101  # assert_used (OK en tests)
```

### Pylint

Crear `.pylintrc`:
```ini
[MASTER]
ignore=migrations,tests.py

[MESSAGES CONTROL]
disable=C0111,  # missing-docstring
        R0903,  # too-few-public-methods

[FORMAT]
max-line-length=100
```

### Vulture

Crear `vulture.ini`:
```ini
[vulture]
min_confidence = 80
paths = apps/
exclude = */migrations/*,*/tests.py
```

## 📈 Visualizar Reportes

### Opción 1: Ver JSON en Terminal

```bash
# Pretty print
cat quality-reports/complexity.json | python -m json.tool

# Con jq (si lo tienes instalado)
cat quality-reports/complexity.json | jq '.'
```

### Opción 2: Abrir en Editor

Los archivos JSON se pueden abrir en Cursor/VS Code para mejor lectura.

### Opción 3: Generar HTML (futuro)

Puedes agregar herramientas como `radon-html` para generar reportes visuales.

## 🚫 Excluir Archivos

Algunos archivos no deben analizarse:

```bash
# Excluir migraciones
radon cc apps/ -e "*/migrations/*"

# Excluir tests
bandit -r apps/ --exclude apps/*/tests.py
```

Ya configurado en el Makefile para excluir automáticamente:
- Migraciones de Django
- Cache de Python
- Archivos temporales

## 🔄 Integración CI/CD (Futuro)

Ejemplo para GitHub Actions:

```yaml
- name: Quality Analysis
  run: |
    make quality
    # Fallar si score de pylint < 8.0
    pylint apps/ --fail-under=8.0
    # Fallar si hay vulnerabilidades HIGH
    bandit -r apps/ -lll --exit-zero
```

## 💡 Tips y Mejores Prácticas

### 1. Ejecuta quality-summary regularmente
```bash
make quality-summary
```
Rápido feedback sin generar archivos.

### 2. Establece umbrales

No permitas que la complejidad crezca:
```bash
# Script personalizado
radon cc apps/ -a -nb | grep "F " && exit 1
```

### 3. Documenta excepciones

Si algo marca false positive:
```python
# nosec - bandit: esto es seguro porque...
password = get_from_env()  # noqa: S105
```

### 4. Prioriza

1. **Urgente**: Vulnerabilidades HIGH
2. **Importante**: Complejidad F, Mantenibilidad C
3. **Bueno tener**: Código muerto, Mejoras menores

### 5. Mejora gradual

No intentes arreglar todo de una vez:
- Semana 1: Vulnerabilidades
- Semana 2: Complejidad > 30
- Semana 3: Código muerto
- Y así...

## 🆚 Alternativa: SonarQube

**¿Cuándo usar SonarQube?**
- Equipos grandes (10+ developers)
- Necesitas dashboards visuales
- Compliance obligatorio
- CI/CD complejo

**Ventajas de nuestra solución:**
- ✅ Gratuito
- ✅ Rápido (segundos vs minutos)
- ✅ Sin infraestructura adicional
- ✅ Funciona offline
- ✅ Fácil de personalizar

**Setup SonarQube (si lo necesitas):**
```bash
# Docker
docker run -d --name sonarqube -p 9000:9000 sonarqube:community

# Analizar
sonar-scanner \
  -Dsonar.projectKey=thenaturalway \
  -Dsonar.sources=apps \
  -Dsonar.host.url=http://localhost:9000
```

Pero para proyectos pequeños/medianos, nuestra solución es suficiente.

## 📚 Referencias

- [Radon Documentation](https://radon.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [Vulture Documentation](https://github.com/jendrikseipp/vulture)
- [Cyclomatic Complexity (Wikipedia)](https://en.wikipedia.org/wiki/Cyclomatic_complexity)
- [Maintainability Index](https://docs.microsoft.com/en-us/visualstudio/code-quality/code-metrics-values)

## ✅ Checklist de Calidad

Antes de cada release, verifica:

```bash
- [ ] make quality ejecutado sin errores críticos
- [ ] No hay vulnerabilidades HIGH
- [ ] Complejidad promedio < 15
- [ ] No hay archivos con mantenibilidad C
- [ ] Código muerto < 5% del proyecto
- [ ] Pylint score > 8.0
- [ ] Test coverage > 80%
```

---

**Última actualización**: 2025-11-29
**Herramientas**: Ruff, Radon, Bandit, Pylint, Vulture
