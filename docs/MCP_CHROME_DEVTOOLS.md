# Chrome DevTools MCP Integration

## Resumen

Este documento describe cómo se integra el **Model Context Protocol (MCP) de Chrome DevTools** en la metodología AIDD de este proyecto Django/DRF.

## ¿Qué es el MCP de Chrome DevTools?

El MCP (Model Context Protocol) de Chrome DevTools es un protocolo que permite a los agentes de IA conectarse directamente a las herramientas de desarrollo del navegador Chrome para:

- **Inspeccionar el DOM real** y estructura HTML renderizada
- **Monitorear la consola** para capturar errores JavaScript y logs
- **Analizar peticiones de red** (requests, responses, headers, tiempos)
- **Hacer debugging en vivo** con breakpoints y stack traces
- **Capturar screenshots** para análisis visual
- **Medir performance** e identificar bottlenecks

## Integración con AIDD

Se ha añadido una **fase opcional "Inspector"** entre Builder y Craftsman:

```
Architect → Builder → [Inspector] → Craftsman → Deploy
```

### Ubicación en la Metodología

- **Fase**: Inspector (opcional)
- **Después de**: Builder (implementación del código)
- **Antes de**: Craftsman (tests formales)
- **Propósito**: Validar integración browser-backend desde perspectiva real del cliente

### Cuándo Usar la Fase Inspector

**✅ Usar cuando**:
- Implementas endpoints de autenticación/autorización
- Tu API será consumida por un frontend web
- Necesitas debuggear CORS, headers, o content-type
- Quieres validar formato de respuestas desde el browser
- Necesitas medir performance desde perspectiva del cliente
- Antes de deployar a producción

**❌ Saltar cuando**:
- Feature es solo backend sin exposición HTTP
- Microservicios internos no accedidos por browsers
- Herramientas de línea de comandos o background jobs

## Estructura de Archivos

### Instrucciones Agnósticas (`.ai/`)

```
.ai/
└── inspector/
    └── i-1.browser-integration.instructions.md
```

**Contenido**: Instrucciones generales sobre cómo validar APIs desde un navegador, independientes de tecnología.

### Reglas Específicas de Django/DRF (`.cursor/rules/`)

```
.cursor/rules/
└── mcp-chrome-devtools.rules.mdc
```

**Contenido**: Configuración específica de Django/DRF, incluyendo:
- Setup de MCP server
- Templates de test pages
- Checklist de validación para CORS, JWT, response formats
- AI prompts específicos para este proyecto
- Integración con el workflow AIDD

### Frontend de Testing

```
frontend-test/
├── index.html    # UI para probar endpoints
├── auth.js       # Gestión de JWT tokens
├── app.js        # Funciones de test
└── README.md     # Instrucciones de uso
```

**Propósito**: Página HTML simple para probar manualmente endpoints desde un navegador real.

## Workflow de Uso

### 1. Setup

```bash
# Instalar MCP Server
npx @modelcontextprotocol/server-chrome-devtools

# Iniciar Chrome con debugging remoto
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Iniciar Django backend
python manage.py runserver

# Abrir test page
open frontend-test/index.html
```

### 2. Conectar AI a DevTools

Configurar MCP en Warp/Cursor para conectar al puerto 9222.

### 3. Solicitar Validación a la IA

**Ejemplo de prompt**:
```
Usa Chrome DevTools MCP para validar el flujo completo de registro y login de usuarios.
Verifica:
1. CORS configurado correctamente
2. Tokens JWT en formato correcto
3. Response format según estándares del proyecto
4. Sin errores en consola
Documenta los issues en docs/features/user-auth/integration-issues.md
```

### 4. Revisión de Issues

La IA documentará problemas encontrados en:
```
docs/features/{feature-slug}/integration-issues.md
```

### 5. Corrección e Iteración

La IA sugerirá fixes en el código Django/DRF para resolver issues.

### 6. Transición a Craftsman

Una vez validada la integración, los issues encontrados informan los test cases formales en la fase Craftsman.

## Checklist de Validación

Para cada endpoint, la IA verificará:

### ✅ CORS Configuration
- Preflight OPTIONS request presente
- Headers CORS correctos en response
- No errores CORS en console

### ✅ JWT Token Flow
- Login retorna access y refresh tokens
- Tokens se almacenan correctamente (localStorage)
- Protected endpoints usan header Authorization
- Token refresh funciona correctamente

### ✅ Response Format
- Success responses siguen formato estándar del proyecto
- Error responses son informativos y consistentes
- Content-Type es `application/json`

### ✅ Performance
- Authentication endpoints < 200ms
- Simple GET requests < 100ms
- Complex queries < 500ms

### ✅ Console
- No errores JavaScript en happy paths
- Warnings son justificables

## Beneficios

### Para el Proyecto
1. **Detecta issues de integración temprano** antes de tests formales
2. **Valida CORS y autenticación** con evidencia real del navegador
3. **Establece baseline de performance** desde perspectiva del cliente
4. **Mejora mensajes de error** haciéndolos más útiles para frontend
5. **Reduce debugging time** al ver comportamiento real vs. esperado

### Para la Metodología AIDD
1. **Complementa Builder y Craftsman** sin duplicar esfuerzos
2. **Aterriza implementación a la realidad** del navegador
3. **Documenta evidencia visual** de problemas
4. **Informa test cases** en fase Craftsman
5. **Valida antes de producción** reduciendo bugs en deploy

## Ejemplo de Issue Report

```markdown
# Integration Issues - User Authentication

## Issue 1: CORS Preflight Failure

**Endpoint**: POST /api/users/login/
**Severity**: Critical
**Browser Evidence**: 
- Console error: "CORS policy: No 'Access-Control-Allow-Origin' header"
- Network tab shows OPTIONS request with 403 status

**Current Behavior**: 
Login request fails with CORS error

**Expected Behavior**: 
OPTIONS preflight should return 200 with appropriate CORS headers

**Suggested Fix**:
```python
# config/settings.py
INSTALLED_APPS = ['corsheaders', ...]
CORS_ALLOW_ALL_ORIGINS = True  # Development only
```

**Status**: ❌ Open
```

## Próximos Pasos

1. **Inmediato**: La estructura ya está creada y documentada
2. **Cuando necesites validación**: Crea la test page usando templates en `.cursor/rules/mcp-chrome-devtools.rules.mdc`
3. **Para usar MCP**: Sigue instrucciones en `frontend-test/README.md`
4. **Integrar en CI/CD**: Considerar automatizar validaciones browser en el futuro

## Recursos

- **Instrucciones agnósticas**: `.ai/inspector/i-1.browser-integration.instructions.md`
- **Reglas de Django/DRF**: `.cursor/rules/mcp-chrome-devtools.rules.mdc`
- **Test page**: `frontend-test/README.md`
- **Metodología actualizada**: `.ai/AIDD.metodology.md`

## Notas Importantes

- Chrome DevTools MCP requiere Chrome corriendo con `--remote-debugging-port=9222`
- La test page NO es frontend de producción, solo para validación
- Los issues encontrados deben convertirse en test cases formales
- Esta fase es **opcional** - úsala estratégicamente cuando aporta valor
- En este proyecto Django backend, el MCP es más útil cuando hay integración con frontend

---

**Última actualización**: 30 Nov 2025  
**Versión**: 1.0  
**Estado**: Documentado y listo para usar
