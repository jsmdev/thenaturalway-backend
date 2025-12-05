# Documentación de API REST - The Natural Way

Este directorio contiene la documentación de las APIs REST del proyecto The Natural Way.

## Documentación Disponible

### OpenAPI/Swagger

- **[Exercises API](./exercises-openapi.yaml)** - Documentación OpenAPI 3.0.3 para la API de ejercicios

## Cómo Usar la Documentación

### Visualizar con Swagger UI

Puedes visualizar la documentación OpenAPI usando Swagger UI:

1. **Online**: Visita [Swagger Editor](https://editor.swagger.io/) y pega el contenido del archivo YAML
2. **Localmente**: Usa herramientas como:
   - [Swagger UI](https://swagger.io/tools/swagger-ui/)
   - [Redoc](https://github.com/Redocly/redoc)
   - [Postman](https://www.postman.com/) (importa el archivo YAML)

### Integración con Django

Para integrar la documentación OpenAPI con Django REST Framework, puedes usar:

- **drf-spectacular**: Genera documentación OpenAPI automáticamente desde el código
- **drf-yasg**: Genera documentación Swagger/OpenAPI

Ejemplo de configuración con `drf-spectacular`:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    # ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'The Natural Way API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

```python
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

## Estructura de Respuestas

Todas las respuestas de la API siguen un formato estándar:

### Respuesta Exitosa

```json
{
  "data": {...},
  "message": "Mensaje opcional",
  "request": {
    "method": "GET",
    "path": "/api/exercises/",
    "host": "api.thenaturalway.com"
  }
}
```

### Respuesta de Error

```json
{
  "error": "Tipo de error",
  "message": "Mensaje descriptivo",
  "request": {
    "method": "POST",
    "path": "/api/exercises/",
    "host": "api.thenaturalway.com"
  }
}
```

## Autenticación

La API utiliza autenticación JWT (JSON Web Tokens). Para autenticarte:

1. Obtén un token mediante el endpoint de login: `POST /api/users/login/`
2. Incluye el token en el header de las peticiones: `Authorization: Bearer <token>`
3. Refresca el token cuando expire usando: `POST /api/users/refresh/`

## Códigos de Estado HTTP

- **200 OK**: Petición exitosa
- **201 Created**: Recurso creado exitosamente
- **204 No Content**: Recurso eliminado exitosamente
- **400 Bad Request**: Error de validación o solicitud incorrecta
- **401 Unauthorized**: No autenticado o token inválido
- **403 Forbidden**: No tiene permisos para realizar la operación
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error interno del servidor

## Convenciones

- Los nombres de campos en la API usan **camelCase** (ej: `primaryMuscleGroup`)
- Los nombres de campos en el modelo usan **snake_case** (ej: `primary_muscle_group`)
- Los endpoints públicos no requieren autenticación
- Los endpoints que modifican datos requieren autenticación
- Solo el creador de un recurso puede actualizarlo o eliminarlo

## Más Información

- [Arquitectura del Proyecto](../ARCHITECTURE.md)
- [Modelo de Dominio](../DOMAIN.md)
- [Documento de Requerimientos](../PRD.md)
