# Plan de Implementación para Biblioteca de Ejercicios

- **Funcionalidad**: 2_biblioteca_de_ejercicios

Implementar la funcionalidad completa para crear y gestionar una biblioteca de ejercicios personalizados mediante una API REST siguiendo la arquitectura en capas del proyecto. El sistema permitirá a los usuarios crear, listar, buscar, filtrar, actualizar y eliminar ejercicios con soporte para filtros avanzados, búsqueda por texto y soft delete.

## Contexto

### Funcional
- [PRD](/docs/PRD.md)
- [DOMAIN](/docs/DOMAIN.md)
- [Issue #3](https://github.com/jsmdev/thenaturalway-backend/issues/3) - Biblioteca de Ejercicios - Crear y gestionar biblioteca de ejercicios personalizados

### Técnico

**Patrones Arquitectónicos**:
- Layered Architecture: Separación clara entre Presentation (Views), Application (Services), Domain (Models) e Infrastructure (Repositories)
- Repository Pattern: Abstracción del acceso a datos con repositorios que encapsulan consultas complejas
- Service Layer Pattern: Lógica de negocio encapsulada en servicios que orquestan operaciones
- RESTful API Design: Recursos como sustantivos, métodos HTTP para acciones, respuestas estructuradas

**Reglas y Convenciones**:
- Arquitectura en capas: Views → Services → Repositories → Models (nunca invertir dependencias)
- Nomenclatura: snake_case para funciones, PascalCase para clases, UPPER_SNAKE_CASE para constantes
- Estructura de respuesta uniforme: `{"data": ..., "message": ..., "request": {...}}`
- Manejo de errores con excepciones de DRF (ValidationError, NotFound, PermissionDenied)
- Type hints en todas las funciones públicas
- Validación en serializadores (validación de entrada) y servicios (reglas de negocio)
- Soft delete mediante `isActive=False` (no eliminación física)
- Permisos públicos: todos pueden leer, solo creador puede editar/eliminar

**Dependencias Técnicas**:
- Django 5.1.7+
- Django REST Framework para API REST
- Django JSONField para `secondaryMuscleGroups` (array de strings)
- No requiere nuevas dependencias externas

**Decisiones de Diseño**:
- Soft delete: Marcar `isActive=False` (no campo `deleted_at`)
- secondaryMuscleGroups: JSONField para array de strings
- Búsqueda: Query params en `/api/exercises/` (no endpoint separado)
- Permisos: Públicos (todos ven, solo creador edita/elimina)

## Tareas del Plan de Implementación

### Capa Domain (Modelos)

- [x] 1. Crear app exercises con estructura básica (__init__.py, apps.py, admin.py, tests.py)
- [x] 2. Crear modelo Exercise en apps/exercises/models.py con todos los campos del dominio (enums, JSONField, ForeignKey)
- [x] 3. Crear y ejecutar migración para modelo Exercise

### Capa Infrastructure (Repositorios)

- [x] 4. Implementar repositorios en apps/exercises/repositories.py (list, get, create, update, delete con filtros y búsqueda)

### Capa Application (Servicios)

- [x] 5. Implementar servicios en apps/exercises/services.py (lógica de negocio, validaciones, permisos)

### Capa Presentation (Serializadores y Vistas)

- [x] 6. Crear serializadores en apps/exercises/serializers.py (ExerciseSerializer, ExerciseCreateSerializer, ExerciseUpdateSerializer)
- [x] 7. Implementar vistas API en apps/exercises/views.py (ViewSet o APIView con todos los endpoints CRUD)
- [x] 8. Crear api_urls.py en apps/exercises/ con rutas para todos los endpoints

### Capa Configuration

- [x] 9. Registrar app exercises en config/settings.py INSTALLED_APPS
- [x] 10. Añadir ruta api/exercises/ en config/urls.py
- [x] 11. Registrar modelo Exercise en apps/exercises/admin.py con configuración apropiada

## Dependencias entre Tareas

- Tarea 2 depende de: 1
- Tarea 3 depende de: 2
- Tarea 4 depende de: 3
- Tarea 5 depende de: 4
- Tarea 6 depende de: 2
- Tarea 7 depende de: 5, 6
- Tarea 8 depende de: 7
- Tarea 9 depende de: 1
- Tarea 10 depende de: 8
- Tarea 11 depende de: 2

## Estimación de Complejidad

- Tarea 1: baja
- Tarea 2: media
- Tarea 3: baja
- Tarea 4: media
- Tarea 5: media
- Tarea 6: media
- Tarea 7: alta
- Tarea 8: baja
- Tarea 9: baja
- Tarea 10: baja
- Tarea 11: baja

## Riesgos y Mitigaciones

- **Riesgo**: Validación compleja de enums y JSONField puede causar errores
  - **Mitigación**: Usar choices de Django para enums, validar JSONField en serializador con validadores personalizados

- **Riesgo**: Consultas N+1 en listado de ejercicios con relación createdBy
  - **Mitigación**: Usar select_related('createdBy') en queryset del repositorio

- **Riesgo**: Permisos mal implementados pueden permitir edición/eliminación por usuarios no autorizados
  - **Mitigación**: Validar permisos en servicio antes de actualizar/eliminar, verificar que createdBy == user

## Criterios de Aceptación por Tarea

### Tarea 1: Crear app exercises con estructura básica

**Criterios de Aceptación**:
- App exercises creada en apps/exercises/
- Archivos __init__.py, apps.py, admin.py, tests.py presentes
- apps.py configurado con nombre correcto

### Tarea 2: Crear modelo Exercise

**Criterios de Aceptación**:
- Modelo Exercise con todos los campos según DOMAIN.md
- Campos con tipos correctos (CharField, TextField, JSONField, ForeignKey, etc.)
- Choices definidos para enums (movementType, primaryMuscleGroup, equipment, difficulty)
- ForeignKey a User con null=True, blank=True
- Índices en campos consultados frecuentemente (name, primaryMuscleGroup, equipment, difficulty, isActive)
- Método __str__ implementado
- Meta class con db_table y verbose_name

### Tarea 3: Crear y ejecutar migración

**Criterios de Aceptación**:
- Migración creada con makemigrations
- Migración ejecutada con migrate
- Tabla exercises creada en base de datos
- Campos e índices creados correctamente

### Tarea 4: Implementar repositorios

**Criterios de Aceptación**:
- list_exercises_repository con soporte para filtros (primaryMuscleGroup, equipment, difficulty, isActive, createdBy)
- Búsqueda por texto en name y description (icontains)
- Ordenamiento por defecto por name
- Optimización con select_related('createdBy')
- get_exercise_by_id_repository retorna Exercise o None
- create_exercise_repository crea ejercicio con createdBy
- update_exercise_repository actualiza campos proporcionados
- delete_exercise_repository realiza soft delete (isActive=False)

### Tarea 5: Implementar servicios

**Criterios de Aceptación**:
- list_exercises_service valida filtros y llama a repositorio
- get_exercise_service obtiene ejercicio, lanza NotFound si no existe
- create_exercise_service valida datos de negocio y crea ejercicio
- update_exercise_service verifica permisos (solo creador) y actualiza
- delete_exercise_service verifica permisos (solo creador) y realiza soft delete
- Todas las funciones con type hints

### Tarea 6: Crear serializadores

**Criterios de Aceptación**:
- ExerciseSerializer (ModelSerializer) con todos los campos
- Campos calculados: createdBy (username o id)
- Read-only: id, createdAt, updatedAt
- ExerciseCreateSerializer con validación de campos requeridos
- ExerciseUpdateSerializer con todos los campos opcionales
- Validación de enums en serializadores
- Validación de JSONField para secondaryMuscleGroups

### Tarea 7: Implementar vistas API

**Criterios de Aceptación**:
- GET /api/exercises/ lista ejercicios con filtros y búsqueda
- GET /api/exercises/{id}/ obtiene detalle de ejercicio
- POST /api/exercises/ crea ejercicio (IsAuthenticated)
- PUT /api/exercises/{id}/ actualiza ejercicio (IsAuthenticated, solo creador)
- DELETE /api/exercises/{id}/ elimina ejercicio (IsAuthenticated, solo creador)
- Respuestas estructuradas según patrón del proyecto
- Manejo de errores apropiado con códigos HTTP correctos

### Tarea 8: Crear api_urls.py

**Criterios de Aceptación**:
- Router o paths configurados para todos los endpoints
- Rutas: exercises/ (lista y crear), exercises/<int:pk>/ (detalle, actualizar, eliminar)
- Nombres de rutas descriptivos

### Tarea 9: Registrar app en settings

**Criterios de Aceptación**:
- apps.exercises añadido a INSTALLED_APPS en config/settings.py

### Tarea 10: Añadir ruta en urls principal

**Criterios de Aceptación**:
- path('api/exercises/', include('apps.exercises.api_urls')) añadido en config/urls.py

### Tarea 11: Registrar modelo en admin

**Criterios de Aceptación**:
- Exercise registrado en admin.py
- list_display configurado con campos relevantes
- list_filter configurado para filtros comunes
- search_fields configurado para búsqueda

## Estado de Implementación

✅ **Todas las tareas han sido completadas**

La funcionalidad de Biblioteca de Ejercicios está completamente implementada y lista para uso. Todos los endpoints están funcionando correctamente con:

- ✅ Modelo Exercise con todos los campos del dominio
- ✅ Repositorios con filtros, búsqueda y optimizaciones
- ✅ Servicios con validaciones y control de permisos
- ✅ Serializadores con validación completa
- ✅ Vistas API con permisos apropiados (AllowAny para GET, IsAuthenticated para POST/PUT/DELETE)
- ✅ URLs configuradas correctamente
- ✅ Admin de Django configurado
- ✅ Integración completa con el resto de la aplicación

### Endpoints Disponibles

- `GET /api/exercises/` - Lista ejercicios (con filtros, búsqueda y ordenamiento)
- `POST /api/exercises/` - Crea nuevo ejercicio (requiere autenticación)
- `GET /api/exercises/{id}/` - Obtiene detalle de un ejercicio
- `PUT /api/exercises/{id}/` - Actualiza ejercicio (requiere autenticación y ser creador)
- `DELETE /api/exercises/{id}/` - Elimina ejercicio (soft delete, requiere autenticación y ser creador)

### Filtros Disponibles

- `primaryMuscleGroup` - Filtra por grupo muscular principal
- `equipment` - Filtra por equipamiento necesario
- `difficulty` - Filtra por nivel de dificultad
- `isActive` - Filtra por estado activo/inactivo
- `createdBy` - Filtra por usuario creador
- `search` - Búsqueda por texto en nombre y descripción
- `ordering` - Ordenamiento por campo (por defecto: name)

> Fin del Plan de Implementación para `2_biblioteca_de_ejercicios`

