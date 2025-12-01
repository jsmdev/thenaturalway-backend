# Frontend Test - The Natural Way API

Este directorio contiene una página HTML simple para probar manualmente los endpoints de la API desde un navegador real. Se utiliza principalmente con **Chrome DevTools MCP** para validación de integración browser-backend.

## Propósito

Esta test page NO es el frontend de producción. Su propósito es:

1. **Validar integración browser-backend**: CORS, headers, JWT tokens
2. **Inspección con DevTools**: Usar Chrome DevTools para ver requests/responses reales
3. **Testing manual rápido**: Probar endpoints sin Postman/Insomnia
4. **Debugging de autenticación**: Ver flujo completo de JWT tokens en localStorage
5. **Medición de performance**: Tiempos de respuesta desde perspectiva del cliente

## Estructura

```
frontend-test/
├── index.html    # Página principal con controles de UI
├── auth.js       # Gestión de tokens JWT y peticiones autenticadas
├── app.js        # Funciones para probar cada endpoint
└── README.md     # Este archivo
```

## Requisitos

- Python 3.13+ (para correr Django backend)
- Google Chrome (para usar con DevTools MCP)
- Backend corriendo en `http://localhost:8000`

## Uso

### Paso 1: Iniciar el Backend

```bash
# Desde la raíz del proyecto
python manage.py runserver
```

El servidor debe estar corriendo en `http://localhost:8000`.

### Paso 2: Abrir la Test Page

Opción A - Archivo local:
```bash
open frontend-test/index.html
```

Opción B - Servir con Python:
```bash
cd frontend-test
python -m http.server 8080
# Abrir http://localhost:8080 en Chrome
```

### Paso 3: Probar Endpoints

**Registro de Usuario**:
1. Modificar email en el campo (debe ser único)
2. Click en "Register User"
3. Ver respuesta en el recuadro

**Login**:
1. Usar credenciales de usuario registrado
2. Click en "Login"
3. Tokens se guardan automáticamente en localStorage
4. Verificar token display en la parte superior

**Profile (requiere autenticación)**:
1. Asegurarse de tener token (hacer login primero)
2. Click en "Get Profile"
3. Debe retornar datos del usuario

**Token Refresh**:
1. Tener refresh token (de un login previo)
2. Click en "Refresh Token"
3. Nuevo access token reemplaza al anterior

### Paso 4: Inspeccionar con DevTools

**Abrir Chrome DevTools** (`Cmd+Option+I` en macOS):

#### Network Tab
- Ver todas las peticiones HTTP
- Inspeccionar headers (Authorization, Content-Type, CORS)
- Ver request/response bodies
- Medir tiempos de respuesta

#### Console Tab
- Ver logs de requests (console.log en auth.js)
- Detectar errores JavaScript
- Warnings de CORS o autenticación

#### Application Tab
- Storage > Local Storage > file://
- Ver `access_token` y `refresh_token`
- Verificar formato JWT
- Eliminar manualmente si es necesario

## Uso con Chrome DevTools MCP

### Configuración MCP

**1. Instalar MCP Server**:
```bash
npx @modelcontextprotocol/server-chrome-devtools
```

**2. Iniciar Chrome con remote debugging**:
```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
```

**3. Conectar AI a DevTools**:
- Configurar MCP en Warp/Cursor
- Verificar conexión al puerto 9222

### Ejemplo de Prompts para AI

**Validar CORS**:
```
Conecta a Chrome DevTools y abre frontend-test/index.html. 
Inspecciona la petición POST /api/users/login/ y verifica que los headers CORS sean correctos.
```

**Debugging de Autenticación**:
```
Monitorea la consola mientras hago click en "Get Profile". 
Reporta cualquier error 401 y verifica que el header Authorization esté presente.
```

**Medición de Performance**:
```
Mide el tiempo de respuesta de todos los endpoints de autenticación. 
Identifica cuáles tardan más de 200ms.
```

**Inspección de Tokens**:
```
Verifica que después del login, los tokens JWT se almacenen correctamente en localStorage 
y tengan el formato adecuado (tres partes separadas por puntos).
```

## Endpoints Disponibles

### Autenticación

- **POST** `/api/users/register/` - Registro de nuevo usuario
  - Body: `{"email": "...", "password": "...", "first_name": "..."}`
  - Response: Usuario creado

- **POST** `/api/users/login/` - Login de usuario
  - Body: `{"email": "...", "password": "..."}`
  - Response: `{"data": {"access": "...", "refresh": "..."}}`

- **POST** `/api/users/token/refresh/` - Refrescar access token
  - Body: `{"refresh": "..."}`
  - Response: `{"data": {"access": "..."}}`

### Protegidos (requieren token)

- **GET** `/api/users/profile/` - Obtener perfil del usuario autenticado
  - Header: `Authorization: Bearer <access_token>`
  - Response: Datos del usuario

## Problemas Comunes

### CORS Error

**Síntoma**: Console muestra "CORS policy blocked"

**Solución**: Verificar configuración CORS en `config/settings.py`:
```python
INSTALLED_APPS = ['corsheaders', ...]
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', ...]
CORS_ALLOW_ALL_ORIGINS = True  # Solo en desarrollo
```

### 401 Unauthorized en Profile

**Síntoma**: GET /api/users/profile/ retorna 401

**Causas**:
1. No hiciste login (no hay token)
2. Token expirado (access token dura 60 min)
3. Token inválido (formato incorrecto)

**Solución**: 
- Hacer login nuevamente
- Usar "Refresh Token" si tienes refresh token válido
- Verificar en DevTools > Application > Local Storage

### Network Error

**Síntoma**: Status 0, "Network Error" en response

**Causas**:
1. Backend no está corriendo
2. URL incorrecta en `auth.js`
3. Problemas de red/firewall

**Solución**:
- Verificar que `python manage.py runserver` esté corriendo
- Comprobar que backend responda en http://localhost:8000

### Token No Se Guarda

**Síntoma**: Después de login, token display muestra "No token"

**Causas**:
1. Response no incluye tokens en `data.data.access`
2. Error JavaScript en `auth.js`
3. localStorage bloqueado por navegador

**Solución**:
- Verificar en Console tab errores JavaScript
- Inspeccionar response en Network tab
- Verificar estructura: `{"data": {"access": "...", "refresh": "..."}}`

## Notas de Desarrollo

- **NO usar en producción**: Solo para testing/debugging
- **Tokens en localStorage**: No es la forma más segura, pero suficiente para testing
- **Credenciales hardcoded**: Cambiar antes de commit si son reales
- **CORS Allow All**: Solo en desarrollo, restringir en producción
- **HTTP en localhost**: Usar HTTPS en producción

## Integración con AIDD Workflow

Esta test page se usa principalmente en la **fase Inspector** (opcional):

```
Builder (implementación) 
   ↓
Inspector (validación con browser) ← USO DE ESTA TEST PAGE
   ↓
Craftsman (tests formales)
```

Los issues encontrados aquí deben documentarse en:
```
docs/features/{feature-slug}/integration-issues.md
```

Y luego convertirse en test cases formales en la fase Craftsman.

## Recursos

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Model Context Protocol](https://github.com/modelcontextprotocol)
- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

## Mantenimiento

Cuando se añadan nuevos endpoints a la API:

1. Añadir sección HTML en `index.html`
2. Crear función de test en `app.js`
3. Actualizar este README con el nuevo endpoint
4. Documentar en `.cursor/rules/mcp-chrome-devtools.rules.mdc` si es necesario
