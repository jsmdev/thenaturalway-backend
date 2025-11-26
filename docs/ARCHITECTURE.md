# Arquitectura del Proyecto - The Natural Way Backend

Este documento describe la arquitectura del proyecto, incluyendo cómo conviven las interfaces de API REST y Web con templates Django.

## Visión General

El proyecto **The Natural Way Backend** implementa un sistema híbrido que ofrece múltiples interfaces para acceder a la misma funcionalidad:

1. **API REST** (`/api/*`): Endpoints JSON para integración con cualquier frontend externo (React, Vue, Next.js, Laravel, aplicaciones móviles, etc.)
2. **Interfaz Web Django** (`/*`): Vistas Django tradicionales con templates HTML para uso directo en navegador

**Todas las interfaces comparten la misma lógica de negocio**, garantizando consistencia y reutilización de código.

### Múltiples Frontends

El backend está diseñado para soportar **múltiples frontends simultáneamente**:

- **Frontend Django (Templates)**: Interfaz web tradicional servida directamente por Django
- **Frontend Externo 1**: React/Vue/Next.js en proyecto separado consumiendo `/api/*`
- **Frontend Externo 2**: Laravel/PHP en proyecto separado consumiendo `/api/*`
- **Aplicación Móvil**: iOS/Android consumiendo `/api/*`
- **Cualquier otro cliente**: Que consuma la API REST

Todos estos frontends pueden coexistir sin conflictos, ya que:
- Los templates Django usan rutas sin prefijo `/api/*` (ej: `/users/login/`)
- Los frontends externos usan rutas con prefijo `/api/*` (ej: `/api/users/login/`)
- Cada frontend puede usar su propia autenticación (sessions para Django, JWT para externos)

## Arquitectura en Capas

El proyecto sigue una arquitectura en capas clara que separa responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                  │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │   API Views      │      │   Web Views       │        │
│  │  (DRF APIView)   │      │  (Django Views)   │        │
│  │  /api/users/*    │      │  /users/*         │        │
│  └────────┬─────────┘      └────────┬─────────┘        │
│           │                          │                   │
│           └──────────┬───────────────┘                   │
│                      │                                   │
└──────────────────────┼───────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────┐
│                      │                                   │
│            ┌─────────▼─────────┐                         │
│            │   SERIALIZERS     │                         │
│            │   (DRF)           │                         │
│            └─────────┬─────────┘                         │
│                      │                                   │
│            ┌─────────▼─────────┐                         │
│            │     FORMS          │                         │
│            │   (Django Forms)   │                         │
│            └─────────┬─────────┘                         │
│                      │                                   │
└──────────────────────┼───────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────┐
│                      │                                   │
│            ┌─────────▼─────────┐                         │
│            │    SERVICES       │                         │
│            │  (Lógica Negocio) │                         │
│            └─────────┬─────────┘                         │
│                      │                                   │
└──────────────────────┼───────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────┐
│                      │                                   │
│            ┌─────────▼─────────┐                         │
│            │  REPOSITORIES     │                         │
│            │  (Acceso Datos)   │                         │
│            └─────────┬─────────┘                         │
│                      │                                   │
└──────────────────────┼───────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────┐
│                      │                                   │
│            ┌─────────▼─────────┐                         │
│            │     MODELS        │                         │
│            │   (Django ORM)    │                         │
│            └───────────────────┘                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Separación de Responsabilidades

### Capa de Presentación

#### API Views (`apps/{app}/views.py`)
- Manejan peticiones HTTP y respuestas JSON
- Usan serializadores DRF para validación
- Retornan respuestas estructuradas: `{"data": ..., "message": ..., "request": {...}}`
- Autenticación: JWT tokens
- Rutas: `/api/{app}/{resource}/`

#### Web Views (`apps/{app}/web_views.py`)
- Manejan peticiones HTTP y respuestas HTML
- Usan formularios Django para validación
- Renderizan templates HTML
- Autenticación: Django sessions
- Rutas: `/{app}/{resource}/` (sin prefijo `/api/`)

### Capa de Validación

#### Serializers (`apps/{app}/serializers.py`)
- Validan datos de entrada para API REST
- Transforman datos entre API y modelos
- Usados exclusivamente por API Views

#### Forms (`apps/{app}/forms.py`)
- Validan datos de entrada para Web
- Renderizan campos HTML
- Usados exclusivamente por Web Views

### Capa de Lógica de Negocio

#### Services (`apps/{app}/services.py`)
- Contienen la lógica de negocio pura
- Son compartidos por ambas interfaces (API y Web)
- Orquestan operaciones entre repositorios
- Gestionan reglas de negocio y validaciones
- Retornan objetos de datos estructurados o instancias de modelo

### Capa de Acceso a Datos

#### Repositories (`apps/{app}/repositories.py`)
- Gestionan el acceso a datos e integraciones externas
- Retornan instancias de modelo, QuerySets o estructuras de datos simples
- Son la única capa que conoce las fuentes de datos (ORM, APIs externas)

### Capa de Modelos

#### Models (`apps/{app}/models.py`)
- Definen la estructura de datos y reglas de negocio a nivel de base de datos
- Usan Django ORM para persistencia

## Flujo de Datos

### Flujo API REST

```
Request (JSON) 
  → API View (views.py)
    → Serializer (validación)
      → Service (lógica negocio)
        → Repository (acceso datos)
          → Model (ORM)
            → Repository → Service → Serializer → Response (JSON)
```

### Flujo Web

```
Request (HTML Form) 
  → Web View (web_views.py)
    → Form (validación)
      → Service (lógica negocio)
        → Repository (acceso datos)
          → Model (ORM)
            → Repository → Service → Template → Response (HTML)
```

## Estructura de Archivos

Cada funcionalidad (app) tiene la siguiente estructura:

```
apps/{app}/
├── models.py              # Modelos de datos
├── repositories.py        # Acceso a datos
├── services.py            # Lógica de negocio (compartida)
├── serializers.py        # Validación para API
├── forms.py              # Validación para Web
├── views.py               # Vistas API REST
├── web_views.py           # Vistas Web con templates
├── api_urls.py            # URLs para API REST
├── web_urls.py           # URLs para Web
├── templates/
│   └── {app}/
│       ├── {resource}_list.html
│       ├── {resource}_detail.html
│       ├── {resource}_form.html
│       └── ...
└── admin.py               # Configuración Django admin
```

### Apps Implementadas

#### `apps/exercises/` - Biblioteca de Ejercicios

Gestiona la biblioteca de ejercicios disponibles en el sistema.

**Modelos:**
- `Exercise`: Modelo principal con campos para nombre, descripción, tipo de movimiento, grupos musculares, equipamiento, dificultad, instrucciones, URLs de imagen/video, y estado activo.

**Endpoints API REST (`/api/exercises/`):**
- `GET /api/exercises/` - Lista ejercicios con filtros y búsqueda (público)
- `POST /api/exercises/` - Crea un nuevo ejercicio (requiere autenticación)
- `GET /api/exercises/{id}/` - Obtiene detalle de un ejercicio (público)
- `PUT /api/exercises/{id}/` - Actualiza un ejercicio (requiere autenticación + ser creador)
- `DELETE /api/exercises/{id}/` - Elimina un ejercicio soft delete (requiere autenticación + ser creador)

**Endpoints Web (`/exercises/`):**
- `GET /exercises/` - Lista ejercicios (vista web)
- `GET /exercises/{id}/` - Detalle de ejercicio (vista web)
- `GET /exercises/create/` - Formulario de creación
- `GET /exercises/{id}/update/` - Formulario de actualización
- `GET /exercises/{id}/delete/` - Confirmación de eliminación

**Características:**
- Filtrado avanzado por grupo muscular, equipamiento, dificultad, estado y creador
- Búsqueda por texto en nombre y descripción
- Ordenamiento personalizable
- Soft delete (marca `isActive=False` en lugar de eliminar físicamente)
- Control de permisos: solo el creador puede actualizar/eliminar
- Optimización de consultas con `select_related('created_by')` para evitar N+1

**Servicios principales:**
- `list_exercises_service()` - Lista con filtros y búsqueda
- `get_exercise_service()` - Obtiene un ejercicio por ID
- `create_exercise_service()` - Crea un nuevo ejercicio
- `update_exercise_service()` - Actualiza un ejercicio existente
- `delete_exercise_service()` - Realiza soft delete

**Repositorios principales:**
- `list_exercises_repository()` - Consulta con filtros y búsqueda
- `get_exercise_by_id_repository()` - Obtiene por ID
- `create_exercise_repository()` - Crea en base de datos
- `update_exercise_repository()` - Actualiza en base de datos
- `delete_exercise_repository()` - Marca como inactivo

## Autenticación

### API REST
- **Método**: JWT (JSON Web Tokens)
- **Librería**: `djangorestframework-simplejwt`
- **Headers**: `Authorization: Bearer <token>`
- **Endpoints**: `/api/users/login/`, `/api/users/refresh/`, `/api/users/logout/`

### Interfaz Web
- **Método**: Django Session Authentication
- **Middleware**: `django.contrib.auth.middleware.AuthenticationMiddleware`
- **Login**: `/users/login/` (crea sesión)
- **Logout**: `/users/logout/` (destruye sesión)

## URLs y Enrutamiento

### Configuración Principal (`config/urls.py`)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.api_urls')),      # API REST
    path('api/exercises/', include('apps.exercises.api_urls')),  # API REST
    path('users/', include('apps.users.web_urls')),         # Web
    path('exercises/', include('apps.exercises.web_urls')), # Web
]
```

### URLs de App

Cada app tiene dos archivos de URLs separados:

**`apps/{app}/api_urls.py`** - URLs para API REST:
```python
from django.urls import path
from apps.exercises.views import ExerciseListAPIView, ExerciseDetailAPIView

app_name = "exercises_api"

urlpatterns = [
    path("", ExerciseListAPIView.as_view(), name="exercise-list"),
    path("<int:pk>/", ExerciseDetailAPIView.as_view(), name="exercise-detail"),
]
```

**`apps/{app}/web_urls.py`** - URLs para Web:
```python
from django.urls import path
from apps.exercises.web_views import (
    ExerciseListView,
    ExerciseDetailView,
    ExerciseCreateView,
    ExerciseUpdateView,
    ExerciseDeleteView,
)

app_name = "exercises"

urlpatterns = [
    path("", ExerciseListView.as_view(), name="list"),
    path("<int:pk>/", ExerciseDetailView.as_view(), name="detail"),
    path("create/", ExerciseCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ExerciseUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ExerciseDeleteView.as_view(), name="delete"),
]
```

**Nota**: Las rutas API tienen el prefijo `/api/` en la configuración principal (`config/urls.py`), mientras que las rutas web no lo tienen.

## Templates

### Estructura de Templates

```
templates/
├── base.html                    # Template base principal
├── components/                  # Componentes reutilizables
│   ├── header.html
│   ├── footer.html
│   ├── navigation.html
│   └── messages.html
└── includes/                    # Fragmentos reutilizables
    └── forms/

apps/{app}/
└── templates/
    └── {app}/
        ├── {resource}_list.html
        ├── {resource}_detail.html
        ├── {resource}_form.html
        └── ...
```

### Template Base

Todos los templates extienden `base.html` que proporciona:
- Estructura HTML5 semántica
- Navegación común
- Sistema de mensajes (success, error, warning, info)
- Bloques extensibles: `title`, `content`, `extra_css`, `extra_js`

## Ventajas de esta Arquitectura

1. **Reutilización de Código**: La lógica de negocio (services y repositories) es compartida entre todas las interfaces
2. **Consistencia**: Las mismas reglas de negocio se aplican en API, Web Django y cualquier frontend externo
3. **Flexibilidad**: Los clientes pueden elegir entre múltiples interfaces según sus necesidades
4. **Escalabilidad**: Pueden añadirse nuevos frontends sin modificar el backend
5. **Mantenibilidad**: Cambios en lógica de negocio solo requieren actualizar services/repositories
6. **Separación de Responsabilidades**: Cada capa tiene un propósito claro y definido
7. **Testabilidad**: Cada capa puede probarse de forma independiente
8. **Multiplataforma**: El mismo backend sirve web, móvil, desktop y cualquier otro cliente

## Convenciones

### Nomenclatura

- **API Views**: `{Resource}APIView` (ej: `UserRegisterAPIView`)
- **Web Views**: `{Resource}View` (ej: `UserRegisterView`)
- **Services**: `{action}_{resource}_service()` (ej: `register_user_service()`)
- **Repositories**: `{action}_{resource}_repository()` (ej: `create_user_repository()`)
- **Templates**: `{resource}_{action}.html` (ej: `user_register.html`)

### Rutas

- **API**: `/api/{app}/{resource}/{action}/`
- **Web**: `/{app}/{resource}/{action}/`

## Ejemplo Completo: Registro de Usuario

### API REST

**Request:**
```http
POST /api/users/register/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "data": {
    "user": {...},
    "tokens": {
      "access": "...",
      "refresh": "..."
    }
  },
  "message": "Usuario registrado correctamente"
}
```

### Interfaz Web

**Request:**
```http
GET /users/register/
```

**Response:** HTML con formulario de registro

**Request:**
```http
POST /users/register/
Content-Type: application/x-www-form-urlencoded

username=johndoe&email=john@example.com&password=securepass123
```

**Response:** HTML con mensaje de éxito o errores de validación

Ambas implementaciones usan el mismo `register_user_service()` internamente.

## Múltiples Frontends Externos

### Arquitectura con Frontends Separados

```
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND DJANGO                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API REST (/api/*)                                   │   │
│  │  - Autenticación: JWT                                │   │
│  │  - Formato: JSON                                     │   │
│  │  - CORS: Configurado para múltiples orígenes        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Templates Django (/*)                               │   │
│  │  - Autenticación: Sessions                           │   │
│  │  - Formato: HTML                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           │                    │                    │
    ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
    │   Frontend  │      │   Frontend  │      │   Frontend  │
    │   React     │      │   Next.js   │      │   Laravel   │
    │   (Proyecto │      │   (Proyecto │      │   (Proyecto │
    │   separado) │      │   separado) │      │   separado) │
    └─────────────┘      └─────────────┘      └─────────────┘
```

### Consideraciones Técnicas para Frontends Externos

#### CORS (Cross-Origin Resource Sharing)

Para que frontends externos puedan consumir la API desde diferentes dominios, es necesario configurar CORS:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'corsheaders',
]

MIDDLEWARE = [
    # ...
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

# Permitir múltiples orígenes
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React dev server
    "http://localhost:3001",      # Next.js dev server
    "https://app.thenaturalway.com",  # Producción React
    "https://web.thenaturalway.com",  # Producción Next.js
]

# O permitir todos los orígenes en desarrollo (NO en producción)
# CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
```

#### Autenticación JWT para Frontends Externos

Los frontends externos deben:

1. **Login**: `POST /api/users/login/` → Recibe `access` y `refresh` tokens
2. **Almacenar tokens**: En localStorage, sessionStorage o cookies (según preferencia)
3. **Incluir token en requests**: Header `Authorization: Bearer <access_token>`
4. **Refrescar token**: `POST /api/users/refresh/` cuando el access token expire
5. **Logout**: `POST /api/users/logout/` → Invalida refresh token

**Ejemplo en React:**
```javascript
// Login
const response = await fetch('https://api.thenaturalway.com/api/users/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});
const { data } = await response.json();
localStorage.setItem('access_token', data.tokens.access);
localStorage.setItem('refresh_token', data.tokens.refresh);

// Requests autenticados
const response = await fetch('https://api.thenaturalway.com/api/users/me/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

#### Separación de Dominios

**Recomendación de arquitectura:**

- **Backend Django**: `api.thenaturalway.com` o `backend.thenaturalway.com`
- **Frontend React**: `app.thenaturalway.com` o `react.thenaturalway.com`
- **Frontend Next.js**: `web.thenaturalway.com` o `next.thenaturalway.com`
- **Templates Django**: `admin.thenaturalway.com` o `legacy.thenaturalway.com`

Cada frontend puede estar en:
- Diferentes servidores
- Diferentes tecnologías
- Diferentes equipos de desarrollo
- Diferentes ciclos de despliegue

### Ejemplo: Convivencia de Múltiples Frontends

**Escenario Real:**

1. **Templates Django** (`/users/*`): 
   - Usado por administradores internos
   - Autenticación por sesiones
   - Acceso: `admin.thenaturalway.com`

2. **Frontend React** (`/api/*`):
   - Aplicación web moderna para usuarios finales
   - Autenticación JWT
   - Acceso: `app.thenaturalway.com`
   - Desarrollado por equipo frontend separado

3. **Frontend Next.js** (`/api/*`):
   - Versión mejorada con SSR
   - Autenticación JWT
   - Acceso: `web.thenaturalway.com`
   - Migración gradual desde React

4. **App Móvil** (`/api/*`):
   - iOS y Android
   - Autenticación JWT
   - Mismo backend, diferentes apps nativas

**Todos consumen la misma API REST y comparten la misma lógica de negocio.**

## Referencias

- [PRD](./PRD.md) - Documento de Requerimientos del Producto
- [DOMAIN](./DOMAIN.md) - Modelo de Dominio
- [API Documentation](./api/README.md) - Documentación de APIs REST
- [Reglas de Templates Django](../.cursor/rules/django-templates.mdc)
- [Reglas de API Django](../.cursor/rules/api-structure-django.mdc)

