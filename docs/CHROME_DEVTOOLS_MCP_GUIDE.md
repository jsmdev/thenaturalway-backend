# Guía Completa: Chrome DevTools MCP en The Natural Way

## Tabla de Contenidos

1. [¿Qué es el MCP de Chrome DevTools?](#qué-es-el-mcp-de-chrome-devtools)
2. [¿Para qué sirve en este proyecto?](#para-qué-sirve-en-este-proyecto)
3. [Capacidades y Funcionalidades](#capacidades-y-funcionalidades)
4. [Integración en la Metodología AIDD](#integración-en-la-metodología-aidd)
5. [Setup y Configuración](#setup-y-configuración)
6. [Uso Práctico Paso a Paso](#uso-práctico-paso-a-paso)
7. [Casos de Uso Específicos](#casos-de-uso-específicos)
8. [Flujo de Trabajo Completo](#flujo-de-trabajo-completo)
9. [Ejemplos Reales](#ejemplos-reales)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [Referencias](#referencias)

---

## ¿Qué es el MCP de Chrome DevTools?

### Definición

**MCP (Model Context Protocol)** es un protocolo abierto que permite que los agentes de IA (como los asistentes en Warp o Cursor) se conecten directamente a herramientas externas para obtener contexto en tiempo real.

**Chrome DevTools MCP** es una implementación específica que conecta la IA con las Chrome Developer Tools, permitiéndole:

- **Ver** lo que tú ves en el navegador
- **Inspeccionar** peticiones HTTP reales
- **Monitorear** errores en la consola
- **Analizar** el rendimiento de la aplicación
- **Capturar** evidencia visual de problemas

### Diferencia Clave

**Sin MCP**:
```
Usuario: "Mi login no funciona"
IA: "Posiblemente sea un problema de CORS. Revisa los headers..."
      ↑ (Adivina basándose en experiencia general)
```

**Con MCP**:
```
Usuario: "Mi login no funciona"
IA: [conecta a Chrome DevTools]
    [inspecciona Network tab]
    [ve error real en Console]
IA: "Veo un error 401 con mensaje 'Invalid token format'.
     El header Authorization está enviando 'Token abc'
     pero debería ser 'Bearer abc'. Aquí está el fix..."
      ↑ (Diagnostica con evidencia real)
```

---

## ¿Para qué sirve en este proyecto?

### Contexto del Proyecto

**The Natural Way** es una API backend Django REST Framework que será consumida por un frontend web. El backend maneja:

- Autenticación JWT
- Endpoints protegidos con tokens
- Respuestas en formato JSON estandarizado
- CORS para permitir peticiones desde el navegador

### Problemas que Resuelve el MCP

#### 1. **Validación de Integración Browser-Backend**

**Problema**: El backend funciona con Postman, pero falla desde el navegador.

**Solución con MCP**: La IA puede ver exactamente qué pasa cuando el navegador hace la petición:
- ¿Se envían los headers correctos?
- ¿Hay errores CORS?
- ¿El token JWT está bien formateado?

#### 2. **Debugging de Autenticación JWT**

**Problema**: Los tokens JWT no funcionan correctamente.

**Solución con MCP**: La IA inspecciona:
- Si el token se guarda en localStorage
- Si el formato del token es correcto (3 partes separadas por puntos)
- Si el header `Authorization: Bearer <token>` se envía
- Si el token expira y el refresh funciona

#### 3. **Validación de CORS**

**Problema**: "CORS policy blocked" en la consola del navegador.

**Solución con MCP**: La IA verifica:
- Si el preflight OPTIONS request se hace
- Si los headers CORS están en la respuesta
- Si el backend está configurado correctamente

#### 4. **Formato de Respuestas**

**Problema**: El frontend espera un formato pero el backend envía otro.

**Solución con MCP**: La IA compara:
- Response real del backend
- Formato esperado según documentación
- Sugiere cambios necesarios

#### 5. **Performance Baseline**

**Problema**: No sabemos si la API es suficientemente rápida.

**Solución con MCP**: La IA mide:
- Tiempo de respuesta de cada endpoint
- Identifica endpoints lentos (>500ms)
- Detecta N+1 queries u otros bottlenecks

---

## Capacidades y Funcionalidades

### Lo que la IA puede hacer con MCP

#### 📡 Network Inspection

```
✅ Ver todas las peticiones HTTP (GET, POST, PUT, DELETE)
✅ Inspeccionar request headers y body
✅ Analizar response headers y body
✅ Medir tiempo de respuesta (latency)
✅ Detectar errores HTTP (401, 403, 404, 500)
✅ Verificar CORS preflight requests
✅ Monitorear WebSocket connections
```

#### 🖥️ Console Monitoring

```
✅ Capturar errores JavaScript
✅ Ver warnings y logs
✅ Detectar errores de red
✅ Identificar problemas de autenticación
✅ Monitorear mensajes personalizados (console.log)
```

#### 💾 Storage Inspection

```
✅ Ver localStorage items (tokens JWT)
✅ Inspeccionar sessionStorage
✅ Analizar cookies (valores, secure flags, expiration)
✅ Verificar IndexedDB entries
```

#### 🎨 DOM & Visual Inspection

```
✅ Inspeccionar estructura HTML
✅ Ver estilos CSS aplicados
✅ Capturar screenshots de la página
✅ Analizar elementos renderizados
```

#### ⚡ Performance Analysis

```
✅ Medir tiempo de carga de recursos
✅ Identificar long-running scripts
✅ Analizar memory leaks
✅ Detectar layout shifts
✅ Performance waterfall de requests
```

### Lo que NO puede hacer

```
❌ Modificar código directamente en el navegador (solo inspección)
❌ Interactuar con la UI (clicks, forms) - solo observación
❌ Debuggear código Python del backend (solo el lado del browser)
❌ Ejecutar código arbitrario en el navegador
```

---

## Integración en la Metodología AIDD

### Nueva Fase: Inspector (Opcional)

La metodología AIDD ahora incluye una fase opcional **Inspector** entre Builder y Craftsman:

```
┌─────────────────────────────────────────────────────────────┐
│                    AIDD Extended Workflow                    │
└─────────────────────────────────────────────────────────────┘

ARCHITECT
   ↓
   ├─► PRD.md
   ├─► DOMAIN.md
   └─► GitHub Issues (state: defined)

BUILDER
   ↓
   ├─► Implementation Plan (docs/features/{feature}/plan.md)
   └─► Source Code (apps/)
       (state: implemented)

INSPECTOR ★ (OPCIONAL) ★
   ↓
   ├─► Browser DevTools Inspection (via MCP)
   ├─► Integration Validation
   └─► Integration Issues Report (docs/features/{feature}/integration-issues.md)
       (state: validated)

CRAFTSMAN
   ↓
   ├─► Unit & Integration Tests (apps/*/tests.py)
   ├─► Documentation
   └─► Coverage Report
       (state: documented)

DEPLOY
   ↓
   Production (state: deployed)
```

### ¿Cuándo usar la fase Inspector?

#### ✅ Usar Inspector cuando:

1. **Implementas autenticación/autorización**
   - Login/register endpoints
   - JWT token management
   - Protected routes

2. **Tu API tiene frontend web**
   - CORS debe estar configurado
   - Formato de respuestas debe ser consistente
   - Performance importa para UX

3. **Antes de deployment a producción**
   - Validación final de integración
   - Detectar issues que solo aparecen en browser
   - Asegurar que mensajes de error son útiles

4. **Debugging de problemas de integración**
   - "Funciona en Postman pero no en el navegador"
   - Errores CORS intermitentes
   - Tokens que no se guardan correctamente

#### ❌ Saltar Inspector cuando:

1. **Feature es solo backend**
   - Lógica de negocio pura
   - Background jobs/tasks
   - Database migrations

2. **Microservicio interno**
   - No accedido desde navegadores
   - Solo llamadas server-to-server
   - APIs internas sin CORS

3. **CLI tools**
   - Comandos de terminal
   - Scripts de administración
   - Management commands de Django

### Flujo de Transición de Estados

```python
# Estado inicial después de Builder
feature.state = "implemented"

# Opción 1: Usar Inspector
if feature.needs_browser_validation():
    feature.state = "in_inspection"
    # IA usa MCP para validar
    # Documenta issues en integration-issues.md
    feature.state = "validated"
    # Transición a Craftsman
    feature.state = "in_testing"
else:
    # Opción 2: Saltar Inspector
    feature.state = "in_testing"  # Directamente a Craftsman

# Estado final
feature.state = "documented"
```

---

## Setup y Configuración

### Requisitos Previos

```bash
# Sistema
- macOS / Linux / Windows
- Node.js 18+ (para npx)
- Google Chrome instalado
- Python 3.13+ (para Django backend)

# Proyecto
- Backend Django corriendo en localhost:8000
- Test page creada en frontend-test/
```

### Instalación del MCP Server

```bash
# Instalar Chrome DevTools MCP Server (no requiere instalación global)
npx @modelcontextprotocol/server-chrome-devtools
```

Este comando descarga e instala el servidor MCP temporalmente.

### Configuración de Chrome

**Iniciar Chrome con Remote Debugging**:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug

# Linux
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug

# Windows (PowerShell)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir=C:\Temp\chrome-debug
```

**Importante**:
- `--remote-debugging-port=9222` abre el puerto para MCP
- `--user-data-dir` usa perfil temporal para evitar conflictos

**Verificar conexión**:
```bash
# Abrir en otro navegador
open http://localhost:9222/json
```

Deberías ver un JSON con información de las pestañas abiertas.

### Configuración en Warp

**Archivo de configuración**: `~/.warp/mcp.json`

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-chrome-devtools"
      ],
      "env": {
        "CHROME_REMOTE_DEBUGGING_PORT": "9222"
      }
    }
  }
}
```

**Reiniciar Warp** para aplicar cambios.

### Configuración en Cursor

**Archivo de configuración**: `.cursor/mcp.json` en la raíz del proyecto

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-chrome-devtools"
      ],
      "env": {
        "CHROME_REMOTE_DEBUGGING_PORT": "9222"
      }
    }
  }
}
```

---

## Uso Práctico Paso a Paso

### Paso 1: Preparar el Entorno

```bash
# Terminal 1: Iniciar Chrome con debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug

# Terminal 2: Iniciar Django backend
cd /path/to/thenaturalway-backend
python manage.py runserver

# Terminal 3: Warp con IA
# (Aquí interactúas con la IA)
```

### Paso 2: Crear/Abrir Test Page

Si no existe, crear usando los templates en `.cursor/rules/mcp-chrome-devtools.rules.mdc`:

```bash
# Estructura mínima
mkdir -p frontend-test
cd frontend-test

# Copiar templates de .cursor/rules/mcp-chrome-devtools.rules.mdc
# - index.html
# - auth.js
# - app.js
```

**Abrir test page en Chrome** (el que tiene debugging habilitado):

```bash
open frontend-test/index.html
```

### Paso 3: Conectar IA a DevTools

**En Warp o Cursor**, escribe:

```
Conecta a Chrome DevTools en el puerto 9222
```

La IA responderá confirmando la conexión y mostrando las pestañas disponibles.

### Paso 4: Solicitar Validación

**Ejemplo de prompt completo**:

```
Estoy en la fase Inspector del workflow AIDD después de implementar
el feature de autenticación de usuarios.

Usa Chrome DevTools MCP para:

1. Inspeccionar el flujo completo de registro de usuario
   - POST /api/users/register/
   - Verificar response format
   - Verificar status code 201

2. Inspeccionar el flujo de login
   - POST /api/users/login/
   - Verificar que retorna access y refresh tokens
   - Verificar que se guardan en localStorage

3. Validar endpoint protegido
   - GET /api/users/profile/
   - Verificar que usa header Authorization: Bearer <token>
   - Verificar status 200 con token válido
   - Verificar status 401 sin token

4. Validar CORS
   - Verificar preflight OPTIONS requests
   - Verificar headers Access-Control-Allow-*

5. Medir performance
   - Tiempo de respuesta de cada endpoint
   - Identificar si alguno tarda >200ms

Documenta todos los issues encontrados en:
docs/features/user-auth/integration-issues.md

Usa este formato para cada issue:
- Endpoint
- Severidad (Critical/High/Medium/Low)
- Browser Evidence (console errors, network tab)
- Current Behavior
- Expected Behavior
- Suggested Fix (código Django/DRF)
```

### Paso 5: Revisión de Issues

La IA generará un documento como:

```markdown
# Integration Issues - User Authentication

Generated: 2025-12-01
Status: In Review

## Summary
- Total Issues: 3
- Critical: 1
- High: 1
- Medium: 1
- Low: 0

---

## Issue 1: CORS Preflight Failure ⚠️ CRITICAL

**Endpoint**: POST /api/users/login/
**Severity**: Critical
**Status**: 🔴 Open

**Browser Evidence**:
```
Console Error:
Access to fetch at 'http://localhost:8000/api/users/login/' from origin 'null'
has been blocked by CORS policy: Response to preflight request doesn't pass
access control check: No 'Access-Control-Allow-Origin' header is present.

Network Tab:
OPTIONS /api/users/login/ - Status: 403
```

**Current Behavior**:
Login request fails with CORS error. OPTIONS preflight returns 403.

**Expected Behavior**:
OPTIONS preflight should return 200 with CORS headers.

**Suggested Fix**:
```python
# config/settings.py

# 1. Install django-cors-headers
# pip install django-cors-headers

# 2. Add to INSTALLED_APPS
INSTALLED_APPS = [
    'corsheaders',
    # ... existing apps
]

# 3. Add to MIDDLEWARE (before CommonMiddleware)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... existing middleware
]

# 4. Configure CORS (development)
CORS_ALLOW_ALL_ORIGINS = True

# 5. Configure CORS (production)
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

**Verification Steps**:
1. Apply fix
2. Restart Django server
3. Reload test page
4. Click "Login" button
5. Verify no CORS error in console
6. Verify OPTIONS request returns 200

---

## Issue 2: Token Not Saved in localStorage ⚠️ HIGH

[... similar format ...]

---

## Issue 3: Slow Response Time ⚠️ MEDIUM

[... similar format ...]
```

### Paso 6: Aplicar Fixes

La IA puede aplicar los fixes directamente:

```
Aplica el fix sugerido para el Issue 1 (CORS)
```

La IA editará `config/settings.py` con los cambios necesarios.

### Paso 7: Re-validación

```
Re-valida el Issue 1 después de aplicar el fix
```

La IA verificará que el problema está resuelto y actualizará el documento.

### Paso 8: Transición a Craftsman

Una vez todos los issues críticos están resueltos:

```
Todos los issues críticos están resueltos.
Transiciona a la fase Craftsman y genera test cases
basados en los issues encontrados en integration-issues.md
```

---

## Casos de Uso Específicos

### Caso 1: Validar Autenticación JWT

**Escenario**: Has implementado login con JWT y quieres asegurar que funciona desde el navegador.

**Prompt para la IA**:
```
Valida el flujo JWT completo:

1. Abre frontend-test/index.html en Chrome
2. Inspecciona el proceso de login:
   - Click en "Login"
   - Verifica request body tiene email y password
   - Verifica response contiene access y refresh tokens
   - Verifica tokens se guardan en localStorage

3. Inspecciona request a endpoint protegido:
   - Click en "Get Profile"
   - Verifica header Authorization: Bearer <token>
   - Verifica response retorna datos del usuario

4. Simula token expirado:
   - Modifica access_token en localStorage a valor inválido
   - Click en "Get Profile"
   - Verifica error 401
   - Verifica mensaje de error es claro

Reporta cualquier issue.
```

**Output Esperado**:
- ✅ Tokens se generan correctamente
- ✅ Tokens se almacenan en localStorage
- ✅ Header Authorization se envía
- ❌ **Issue**: Mensaje de error 401 no es descriptivo

### Caso 2: Debuggear CORS

**Escenario**: El frontend muestra "CORS policy blocked".

**Prompt para la IA**:
```
Diagnostica el error CORS:

1. Abre Network tab en DevTools
2. Intenta hacer login desde la test page
3. Inspecciona:
   - ¿Hay una petición OPTIONS antes de POST?
   - ¿Qué status code tiene OPTIONS?
   - ¿Qué headers tiene la response?
   - ¿Hay error en Console?

4. Compara con configuración esperada:
   - Access-Control-Allow-Origin: * (dev) o dominio específico (prod)
   - Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE
   - Access-Control-Allow-Headers: Content-Type, Authorization

Sugiere fix específico para config/settings.py
```

**Output Esperado**:
- Diagnosis exacta del problema
- Headers presentes vs. esperados
- Código de fix para Django

### Caso 3: Medir Performance

**Escenario**: Quieres establecer baseline de performance.

**Prompt para la IA**:
```
Mide performance de todos los endpoints de autenticación:

Para cada endpoint:
- POST /api/users/register/
- POST /api/users/login/
- GET /api/users/profile/
- POST /api/users/token/refresh/

Ejecuta cada uno 5 veces y reporta:
- Tiempo promedio de respuesta
- Tiempo mínimo
- Tiempo máximo
- Tamaño del payload (request y response)

Identifica endpoints que tarden más de 200ms.
Para los lentos, sugiere optimizaciones posibles.
```

**Output Esperado**:
```
Performance Report - User Authentication Endpoints

POST /api/users/register/
  Avg: 156ms | Min: 142ms | Max: 178ms
  Request size: 85 bytes | Response size: 234 bytes
  Status: ✅ GOOD

POST /api/users/login/
  Avg: 145ms | Min: 138ms | Max: 156ms
  Request size: 67 bytes | Response size: 512 bytes
  Status: ✅ GOOD

GET /api/users/profile/
  Avg: 523ms | Min: 498ms | Max: 567ms
  Request size: 45 bytes | Response size: 1.2KB
  Status: ⚠️ SLOW (>200ms)

Suggested optimizations for /api/users/profile/:
- Add select_related() for user relationships
- Use only() to limit fields fetched
- Add database index on frequently queried fields
```

### Caso 4: Validar Formato de Respuestas

**Escenario**: Quieres asegurar consistencia en formatos de respuesta.

**Prompt para la IA**:
```
Valida que todos los endpoints siguen el formato estándar del proyecto:

Formato esperado (success):
{
  "data": { /* payload */ },
  "request": { "method": "GET", "path": "/api/...", "host": "..." },
  "message": "..." (opcional)
}

Formato esperado (error):
{
  "error": "Error Type",
  "message": "Human-readable message",
  "request": { "method": "POST", "path": "/api/...", "host": "..." }
}

Inspecciona responses de:
- POST /api/users/register/ (success y error)
- POST /api/users/login/ (success y error)
- GET /api/users/profile/ (success y error 401)

Reporta cualquier desviación del formato.
```

**Output Esperado**:
- Lista de endpoints que cumplen formato
- Lista de endpoints que NO cumplen formato
- Ejemplos de respuestas incorrectas
- Código de fix sugerido

### Caso 5: Inspeccionar Token Expiration

**Escenario**: Quieres verificar que el refresh token funciona cuando el access token expira.

**Prompt para la IA**:
```
Valida el flujo de refresh token:

1. Hacer login y guardar tokens
2. Inspeccionar access token en localStorage:
   - Decodifica el JWT (payload)
   - Verifica claim 'exp' (expiration)
   - Calcula tiempo hasta expiración

3. Simular expiración:
   - Modificar 'exp' a timestamp pasado
   - Guardar token modificado en localStorage
   - Intentar GET /api/users/profile/

4. Verificar refresh flow:
   - POST /api/users/token/refresh/ con refresh token
   - Verificar nuevo access token
   - Verificar nuevo token funciona

Reporta issues en el flujo.
```

---

## Flujo de Trabajo Completo

### Workflow Detallado con MCP

```
┌──────────────────────────────────────────────────────────────────┐
│ FASE BUILDER (Implementación)                                    │
└──────────────────────────────────────────────────────────────────┘

1. IA implementa feature según plan
2. Código committeado (sin push)
3. Feature state: "implemented"

         ↓

┌──────────────────────────────────────────────────────────────────┐
│ TRANSICIÓN A INSPECTOR                                           │
└──────────────────────────────────────────────────────────────────┘

Developer decide: ¿Necesita validación browser?

  YES → Continúa a Inspector
  NO  → Salta a Craftsman

         ↓ (YES)

┌──────────────────────────────────────────────────────────────────┐
│ FASE INSPECTOR (Validación Browser)                             │
└──────────────────────────────────────────────────────────────────┘

A. SETUP
   ├─ Developer inicia Chrome con --remote-debugging-port=9222
   ├─ Developer inicia Django backend (python manage.py runserver)
   ├─ Developer abre test page en Chrome
   └─ Developer solicita a IA: "Conecta a Chrome DevTools"

B. INSPECCIÓN
   ├─ IA conecta a DevTools via MCP
   ├─ IA inspecciona Network tab durante operaciones
   ├─ IA monitorea Console durante operaciones
   ├─ IA revisa Storage (localStorage, cookies)
   ├─ IA mide tiempos de respuesta
   └─ IA captura screenshots si hay errores visuales

C. DOCUMENTACIÓN
   ├─ IA genera integration-issues.md
   ├─ IA categoriza issues (Critical/High/Medium/Low)
   ├─ IA incluye evidencia (console logs, network details)
   ├─ IA sugiere fixes específicos de Django/DRF
   └─ IA prioriza issues

D. CORRECCIÓN
   ├─ IA aplica fixes para issues críticos
   ├─ Developer revisa cambios
   ├─ IA re-valida después de cada fix
   └─ Repite hasta que no hay issues críticos

E. QUALITY GATE
   ├─ ✅ No issues críticos pendientes
   ├─ ✅ CORS configurado correctamente
   ├─ ✅ Autenticación funciona end-to-end
   ├─ ✅ Response formats son consistentes
   ├─ ✅ No errores JavaScript en happy paths
   └─ ✅ Performance dentro de thresholds

         ↓ (Quality Gate PASSED)

┌──────────────────────────────────────────────────────────────────┐
│ TRANSICIÓN A CRAFTSMAN                                           │
└──────────────────────────────────────────────────────────────────┘

1. Feature state: "validated"
2. integration-issues.md entregado
3. Developer solicita: "Transiciona a Craftsman"

         ↓

┌──────────────────────────────────────────────────────────────────┐
│ FASE CRAFTSMAN (Tests Formales)                                 │
└──────────────────────────────────────────────────────────────────┘

A. TEST GENERATION
   ├─ IA lee integration-issues.md
   ├─ IA convierte cada issue en test case
   ├─ IA genera unit tests (apps/*/tests.py)
   └─ IA genera integration tests

B. DOCUMENTATION
   ├─ IA documenta APIs públicas
   ├─ IA actualiza STRUCTURE.md si es necesario
   └─ IA genera coverage report

C. QUALITY GATE
   ├─ ✅ Test coverage >80%
   ├─ ✅ Todos los tests pasan
   └─ ✅ Documentación completa

         ↓

┌──────────────────────────────────────────────────────────────────┐
│ DEPLOY                                                           │
└──────────────────────────────────────────────────────────────────┘

Feature state: "documented" → "deployed"
```

### Diagrama de Decisión

```
                     ┌─────────────────┐
                     │  BUILDER DONE   │
                     └────────┬────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ ¿Feature expone  │
                    │  API a browser?  │
                    └──────┬───────────┘
                           │
              ┌────────────┴────────────┐
             YES                        NO
              │                          │
              ▼                          ▼
    ┌──────────────────┐      ┌──────────────────┐
    │  ¿Feature tiene  │      │  SKIP INSPECTOR  │
    │  autenticación?  │      │   ↓ CRAFTSMAN    │
    └────────┬─────────┘      └──────────────────┘
             │
        ┌────┴────┐
       YES       NO
        │         │
        ▼         ▼
     ┌─────┐  ┌──────────────────┐
     │ USE │  │ ¿Pre-deployment  │
     │ MCP │  │    validation?   │
     └─────┘  └────────┬─────────┘
                       │
                  ┌────┴────┐
                 YES       NO
                  │         │
                  ▼         ▼
              ┌─────┐   ┌──────────┐
              │ USE │   │   SKIP   │
              │ MCP │   │ INSPECTOR│
              └─────┘   └──────────┘
```

---

## Ejemplos Reales

### Ejemplo 1: Detectando Error de Token Format

**Situación**: El login funciona en Postman pero falla desde el navegador.

**Conversación con IA**:

```
👤 User:
He implementado el login JWT pero cuando lo pruebo desde el navegador
me da 401. En Postman funciona perfectamente. ¿Puedes ayudarme?

🤖 IA:
Voy a conectarme a Chrome DevTools para ver qué está pasando exactamente.

[IA conecta a DevTools via MCP]
[IA inspecciona Network tab]

Encontré el problema. En la petición desde el navegador, el header
Authorization está siendo enviado como:

  Authorization: Token eyJhbGc...

Pero tu backend Django REST Framework espera:

  Authorization: Bearer eyJhbGc...

En auth.js línea 170, estás usando:
  headers['Authorization'] = `Token ${accessToken}`;

Debería ser:
  headers['Authorization'] = `Bearer ${accessToken}`;

¿Quieres que haga el cambio?

👤 User:
Sí, por favor

🤖 IA:
[IA edita frontend-test/auth.js]

Listo. He cambiado "Token" por "Bearer".
Recarga la página y vuelve a intentar el login.

[User recarga y hace login]

🤖 IA:
[IA monitorea Network tab]

Perfecto. Ahora veo:
✅ POST /api/users/login/ - Status 200
✅ Response contiene access y refresh tokens
✅ Tokens guardados en localStorage
✅ GET /api/users/profile/ - Status 200 (con nuevo token)

El issue está resuelto. Lo documento en integration-issues.md
para que se cree un test case en la fase Craftsman.
```

### Ejemplo 2: Optimizando Endpoint Lento

**Situación**: El endpoint de perfil tarda demasiado.

**Conversación con IA**:

```
👤 User:
El endpoint /api/users/profile/ se siente lento.
¿Puedes medir cuánto tarda exactamente?

🤖 IA:
[IA conecta a DevTools]
[IA ejecuta GET /api/users/profile/ múltiples veces]

Mediciones del endpoint GET /api/users/profile/:
- Intento 1: 678ms
- Intento 2: 645ms
- Intento 3: 701ms
- Intento 4: 663ms
- Intento 5: 689ms

Promedio: 675ms

Esto es significativamente más lento que el threshold recomendado
de <200ms para endpoints simples de lectura.

Voy a inspeccionar el código del endpoint para identificar el problema...

[IA lee apps/users/views.py]
[IA lee apps/users/serializers.py]

Encontré el problema. En UserProfileSerializer estás usando:

```python
class UserProfileSerializer(serializers.ModelSerializer):
    workouts = WorkoutSerializer(many=True)  # ← Esto causa N+1
    routines = RoutineSerializer(many=True)  # ← Esto también
```

Cada serializer de relación hace queries adicionales. Para un usuario
con 10 workouts y 5 routines, estás haciendo:
- 1 query para el usuario
- 10 queries para workouts
- 5 queries para routines
Total: 16 queries

Solución sugerida:

```python
# apps/users/repositories.py
def get_user_profile_repository(user_id: int) -> Optional[User]:
    return User.objects.select_related(
        'subscription'
    ).prefetch_related(
        'workouts',
        'routines'
    ).get(id=user_id)
```

Esto reduce las queries de 16 a 3 (user + workouts en batch + routines en batch).

¿Quieres que aplique el fix?

👤 User:
Sí, aplícalo

🤖 IA:
[IA edita apps/users/repositories.py]

Aplicado. Reinicia el servidor Django y vuelve a recargar la página.

[User reinicia servidor y recarga]

🤖 IA:
[IA mide nuevamente]

Nuevas mediciones:
- Intento 1: 145ms
- Intento 2: 138ms
- Intento 3: 152ms
- Intento 4: 141ms
- Intento 5: 148ms

Promedio: 145ms ✅

Mejora: 78% más rápido (de 675ms a 145ms)

El endpoint ahora está dentro del threshold recomendado.
Documento esta optimización en integration-issues.md
```

### Ejemplo 3: Validando Flujo Completo de Auth

**Situación**: Primera vez usando Inspector para validar autenticación.

**Conversación con IA**:

```
👤 User:
He terminado de implementar el feature de autenticación JWT.
Estoy en la fase Inspector. Por favor valida el flujo completo.

🤖 IA:
Perfecto. Voy a validar el flujo de autenticación end-to-end usando
Chrome DevTools MCP.

[IA conecta a DevTools]
[IA abre frontend-test/index.html]

FASE 1: Validación de Registro
[IA simula click en "Register User"]
[IA inspecciona Network]

✅ POST /api/users/register/
   Status: 201 Created
   Response format: ✅ Correcto
   {
     "data": {
       "id": 1,
       "email": "test@example.com",
       "first_name": "Test"
     },
     "request": {...}
   }

FASE 2: Validación de Login
[IA simula click en "Login"]
[IA inspecciona Network]

✅ POST /api/users/login/
   Status: 200 OK
   Response contiene tokens: ✅
   {
     "data": {
       "access": "eyJhbGc...",
       "refresh": "eyJhbGc..."
     }
   }

[IA inspecciona Application > Local Storage]

✅ Tokens guardados en localStorage:
   - access_token: present (JWT format valid)
   - refresh_token: present (JWT format valid)

FASE 3: Validación de Endpoint Protegido
[IA simula click en "Get Profile"]
[IA inspecciona Network]

✅ GET /api/users/profile/
   Status: 200 OK
   Header Authorization: Bearer eyJhbGc... ✅
   Response: User profile data ✅

FASE 4: Validación de CORS
[IA inspecciona todas las requests]

⚠️ ISSUE DETECTADO: CORS no configurado

Console Error:
"Access to fetch at 'http://localhost:8000/api/users/login/'
from origin 'null' has been blocked by CORS policy"

Explicación:
- El navegador hace preflight OPTIONS request
- El backend retorna 403 Forbidden
- Falta configuración de django-cors-headers

Severity: CRITICAL (bloquea funcionamiento desde browser)

Fix sugerido:
[... código de fix ...]

¿Quieres que aplique el fix ahora?

👤 User:
Sí, aplícalo

🤖 IA:
[IA instala django-cors-headers]
[IA edita config/settings.py]
[IA reinicia servidor Django]

Fix aplicado. Recarga la página y vuelve a probar.

[User recarga y hace login]

🤖 IA:
[IA monitorea nuevamente]

✅ CORS configurado correctamente
   OPTIONS /api/users/login/ - Status: 200
   Header Access-Control-Allow-Origin: * ✅
   Header Access-Control-Allow-Methods: POST, GET, OPTIONS ✅

FASE 5: Validación de Performance
[IA mide tiempos]

Performance Summary:
- POST /api/users/register/: 156ms ✅
- POST /api/users/login/: 142ms ✅
- GET /api/users/profile/: 138ms ✅

Todos los endpoints están dentro del threshold de 200ms.

FASE 6: Validación de Token Refresh
[IA simula expiración de access token]
[IA click en "Refresh Token"]

✅ POST /api/users/token/refresh/
   Status: 200 OK
   Nuevo access token recibido ✅
   Token actualizado en localStorage ✅

═══════════════════════════════════════════════════════════

RESUMEN DE VALIDACIÓN

✅ Registro de usuario funciona correctamente
✅ Login funciona y retorna tokens válidos
✅ Tokens se guardan en localStorage
✅ Endpoints protegidos usan Authorization header
✅ CORS configurado (después de fix)
✅ Performance dentro de thresholds
✅ Token refresh funciona correctamente
✅ Formatos de respuesta son consistentes
✅ No hay errores JavaScript en console

Issues Encontrados: 1
- Issue #1: CORS no configurado (RESUELTO)

Documentación generada en:
docs/features/user-auth/integration-issues.md

Quality Gate: ✅ PASSED

El feature está listo para transicionar a la fase Craftsman.
```

---

## Troubleshooting

### Problema 1: IA no puede conectar a DevTools

**Síntoma**:
```
Error: Unable to connect to Chrome DevTools on port 9222
```

**Causas posibles**:

1. **Chrome no está corriendo con debugging habilitado**
   ```bash
   # Verificar si el puerto está abierto
   lsof -i :9222

   # Si no hay output, Chrome no está en modo debug
   ```

2. **Otro proceso usa el puerto 9222**
   ```bash
   # Ver qué proceso usa el puerto
   lsof -i :9222
   # Matar proceso si es necesario
   kill -9 <PID>
   ```

3. **Chrome ya estaba abierto antes de iniciar con debugging**
   ```bash
   # Cerrar todos los procesos de Chrome
   killall "Google Chrome"

   # Reiniciar con debugging
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=9222 \
     --user-data-dir=/tmp/chrome-debug
   ```

**Solución**:
```bash
# Script completo para reiniciar Chrome
killall "Google Chrome"
sleep 2
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug &
sleep 2
open http://localhost:9222/json  # Verificar conexión
```

### Problema 2: Test Page muestra Network Error

**Síntoma**:
```
Status: 0
Error: Network Error
message: "Failed to fetch"
```

**Causas**:

1. **Backend no está corriendo**
   ```bash
   # Verificar que Django está corriendo
   ps aux | grep "manage.py runserver"

   # O intentar curl
   curl http://localhost:8000/api/
   ```

2. **Puerto incorrecto en auth.js**
   ```javascript
   // auth.js - verificar URL
   const API_URL = 'http://localhost:8000/api';  // ← Debe coincidir con backend
   ```

3. **Firewall bloqueando conexión**
   ```bash
   # Temporalmente desactivar firewall (macOS)
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
   ```

**Solución**:
```bash
# 1. Verificar Django
python manage.py runserver
# Output debe mostrar: "Starting development server at http://127.0.0.1:8000/"

# 2. Test con curl
curl http://localhost:8000/api/users/
# Debe retornar respuesta JSON o lista de endpoints

# 3. Si funciona curl pero no browser, es problema CORS (ver Issue #3)
```

### Problema 3: CORS Error Persiste

**Síntoma**:
```
Console: Access to fetch at 'http://localhost:8000/api/...' from origin 'null'
has been blocked by CORS policy
```

**Verificación**:

```bash
# Test CORS manualmente
curl -X OPTIONS http://localhost:8000/api/users/login/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# Debe incluir en response:
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Methods: POST, OPTIONS
```

**Solución definitiva**:

```python
# config/settings.py

# 1. Asegurar que django-cors-headers está instalado
# pip install django-cors-headers

# 2. INSTALLED_APPS (debe estar ANTES de resto)
INSTALLED_APPS = [
    'corsheaders',  # ← PRIMERO
    'django.contrib.admin',
    # ... resto
]

# 3. MIDDLEWARE (CorsMiddleware debe ser PRIMERO)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ← PRIMERO
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... resto (sin CSRF middleware para APIs)
]

# 4. Configuración CORS
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        "https://yourdomain.com",
    ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

**Reiniciar servidor Django después de cambios**.

### Problema 4: Token JWT no se guarda en localStorage

**Síntoma**:
Token display muestra "No token" después de login exitoso.

**Debug con MCP**:

```
Prompt para IA:
Inspecciona el proceso de login y verifica:
1. Response de /api/users/login/ contiene tokens
2. Función saveTokens() se ejecuta
3. localStorage.setItem() se llama
4. No hay errores JavaScript en console
```

**Causas comunes**:

1. **Response no tiene estructura esperada**
   ```javascript
   // auth.js espera:
   response.data.data.access  // ← Tres niveles

   // Backend puede estar enviando:
   response.data.access       // ← Dos niveles
   ```

2. **localStorage bloqueado**
   - Navegador en modo incógnito
   - Extensiones de privacidad
   - Configuración del navegador

3. **Error JavaScript silencioso**
   ```javascript
   // Añadir try-catch en auth.js
   function saveTokens(access, refresh) {
       try {
           console.log('Saving tokens:', { access, refresh });
           localStorage.setItem('access_token', access);
           localStorage.setItem('refresh_token', refresh);
           console.log('Tokens saved successfully');
       } catch (error) {
           console.error('Error saving tokens:', error);
       }
   }
   ```

**Solución**:
1. Usar MCP para ver response exacta
2. Ajustar auth.js según estructura real
3. Verificar que browser permite localStorage

### Problema 5: Performance Inconsistente

**Síntoma**:
Primer request tarda 800ms, siguientes tardan 150ms.

**Explicación**:
Primera petición incluye:
- Django app startup
- Database connection pooling
- Compilación de templates
- Import de módulos

**No es problema** si:
- Requests subsecuentes son rápidos
- En producción con gunicorn/uwsgi preforked, no hay delay

**Para medir correctamente**:

```
Prompt para IA:
Descarta el primer request y mide los siguientes 10 requests.
Reporta promedio, min, max, y percentil 95.
```

---

## Best Practices

### 1. Cuándo Usar MCP

**✅ Usar MCP para**:
- Validar integración browser-backend ANTES de tests formales
- Debuggear problemas que solo aparecen en browser (CORS, tokens)
- Medir performance desde perspectiva del usuario
- Establecer baseline de performance
- Validar formato de respuestas con evidencia real

**❌ NO usar MCP para**:
- Testing unitario (usar pytest)
- Testing de lógica de negocio (usar Django TestCase)
- Performance profiling de código Python (usar django-silk)
- Security testing (usar herramientas especializadas)

### 2. Secuencia Óptima de Validación

```
1. CORS & Network
   ├─ Verifica preflight requests primero
   ├─ Sin CORS, nada más funcionará
   └─ Fix y re-valida antes de continuar

2. Authentication Flow
   ├─ Register → Login → Store Tokens
   ├─ Usa tokens en protected endpoints
   └─ Verifica refresh token

3. Response Formats
   ├─ Success responses
   ├─ Error responses (400, 401, 403, 404, 500)
   └─ Consistencia en estructura

4. Console Monitoring
   ├─ JavaScript errors
   ├─ Network errors
   └─ Warnings

5. Performance
   ├─ Mide últimos (después de validación funcional)
   └─ Identifica bottlenecks para optimizar

6. Storage & State
   ├─ localStorage/sessionStorage
   ├─ Cookies
   └─ State persistence
```

### 3. Documentación de Issues

**Template recomendado**:

```markdown
## Issue N: [Título Descriptivo] ⚠️ [SEVERITY]

**Endpoint**: [METHOD] /api/path/
**Severity**: Critical | High | Medium | Low
**Status**: 🔴 Open | 🟡 In Progress | 🟢 Resolved

**Browser Evidence**:
```
[Console logs, network tab screenshots, etc.]
```

**Current Behavior**:
[Qué pasa ahora]

**Expected Behavior**:
[Qué debería pasar]

**Root Cause**:
[Análisis técnico del problema]

**Suggested Fix**:
```python
[Código específico del fix]
```

**Verification Steps**:
1. [Paso a paso para verificar el fix]
2. ...

**Related Files**:
- path/to/file.py:line
- path/to/another.py:lines-range

**Status History**:
- 2025-12-01 10:30 - Issue detected by MCP inspection
- 2025-12-01 10:45 - Fix applied
- 2025-12-01 11:00 - Verified resolved
```

### 4. Comunicación con la IA

**Prompts efectivos**:

✅ **Buenos prompts**:
```
"Inspecciona el flujo de login y verifica que los tokens se guarden
en localStorage. Documenta cualquier issue encontrado."

"Mide el tiempo de respuesta de GET /api/users/profile/ ejecutándolo
10 veces. Reporta promedio, min, max y percentil 95."

"Valida que todos los endpoints de autenticación sigan el formato
de respuesta estándar del proyecto definido en WARP.md."
```

❌ **Malos prompts**:
```
"Mira si funciona"  // ← Muy vago

"Arregla los errores"  // ← No específico, la IA no sabe cuáles

"Revisa todo"  // ← Muy amplio, resultados inconsistentes
```

**Estructura ideal**:
```
[Acción] + [Qué inspeccionar] + [Criterios de validación] + [Output esperado]

Ejemplo:
"Inspecciona [el flujo de login] verificando [que tokens se guarden]
según [formato JWT válido]. Documenta [issues en integration-issues.md]."
```

### 5. Quality Gates para Inspector

Antes de pasar a Craftsman, verificar:

```
✅ CORS
   ├─ OPTIONS requests retornan 200
   ├─ Headers Access-Control-* presentes
   └─ No errors CORS en console

✅ Authentication
   ├─ Register/Login retornan tokens válidos
   ├─ Tokens se guardan correctamente
   ├─ Protected endpoints usan Authorization header
   └─ Refresh token funciona

✅ Response Formats
   ├─ Success responses siguen estándar
   ├─ Error responses siguen estándar
   └─ Content-Type es application/json

✅ Performance
   ├─ Auth endpoints < 200ms
   ├─ Simple GETs < 100ms
   └─ Complex queries < 500ms

✅ Console
   ├─ No errors JavaScript
   ├─ No network errors
   └─ Warnings documentados

✅ Documentation
   ├─ integration-issues.md creado
   ├─ Issues categorizados por severidad
   └─ Fixes sugeridos son específicos
```

### 6. Mantenimiento de Test Page

```javascript
// Estructura recomendada de test page

// auth.js - Token management
const API_URL = 'http://localhost:8000/api';
let accessToken = localStorage.getItem('access_token');
let refreshToken = localStorage.getItem('refresh_token');

// Funciones reutilizables
function saveTokens(access, refresh) { }
function clearToken() { }
function updateTokenDisplay() { }
async function apiRequest(endpoint, options) { }

// app.js - Test functions
async function testRegister() { }
async function testLogin() { }
async function testProfile() { }
async function testTokenRefresh() { }

// Añadir nuevos tests aquí cuando se agreguen endpoints
async function testCreateWorkout() { }
async function testListWorkouts() { }
```

**Actualizar cuando**:
- Se añadan nuevos endpoints
- Cambie el formato de autenticación
- Se modifique la estructura de respuestas
- Se implementen nuevas features con UI

---

## Referencias

### Documentación del Proyecto

- **Metodología AIDD**: `.ai/AIDD.metodology.md`
- **Instrucciones Inspector**: `.ai/inspector/i-1.browser-integration.instructions.md`
- **Reglas Django/MCP**: `.cursor/rules/mcp-chrome-devtools.rules.mdc`
- **Test Page**: `frontend-test/README.md`
- **Resumen MCP**: `docs/MCP_CHROME_DEVTOOLS.md`

### Documentación Externa

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Model Context Protocol Specification](https://github.com/modelcontextprotocol/specification)
- [Chrome DevTools MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/chrome-devtools)
- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [Django REST Framework Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [JWT.io - JWT Debugger](https://jwt.io/)

### Recursos de Aprendizaje

- [Using Chrome DevTools for API Testing](https://developer.chrome.com/docs/devtools/network/)
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [Django Performance Optimization](https://docs.djangoproject.com/en/5.1/topics/performance/)

### Herramientas Complementarias

- **Postman**: Para testing manual de APIs (sin browser context)
- **Django Debug Toolbar**: Para profiling de queries Django
- **django-silk**: Para performance profiling detallado
- **Sentry**: Para error tracking en producción

---

## Changelog

### v1.0 - 2025-12-01
- ✨ Documentación inicial completa
- ✨ Integración con metodología AIDD
- ✨ Ejemplos reales de uso
- ✨ Troubleshooting guide
- ✨ Best practices

---

**Mantenido por**: The Natural Way Development Team
**Última actualización**: 2025-12-01
**Versión**: 1.0.0
**Estado**: Production Ready
