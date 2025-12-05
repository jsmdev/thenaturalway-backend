# Plan de Implementación para Registrar Sesiones de Entrenamiento

- **Funcionalidad**: 4_registrar_sesiones_de_entrenamiento

Implementar la funcionalidad completa para registrar y gestionar sesiones de entrenamiento realizadas por los usuarios mediante una API REST y una interfaz web con templates Django, siguiendo la arquitectura en capas del proyecto. El sistema permitirá a los usuarios crear, listar, ver detalle, actualizar y eliminar sesiones de entrenamiento con sus ejercicios asociados. Las sesiones pueden estar vinculadas opcionalmente a una rutina existente y permitirán registrar datos detallados como duración, RPE, nivel de energía, horas de sueño y ejercicios realizados con sus series, repeticiones, pesos y notas.

## Contexto

### Funcional
- [PRD](/docs/PRD.md)
- [DOMAIN](/docs/DOMAIN.md)
- [Issue #5](https://github.com/jsmdev/thenaturalway-backend/issues/5) - Registrar Sesiones de Entrenamiento - Registrar y documentar sesiones de entrenamiento completadas con datos detallados

### Técnico

**Patrones Arquitectónicos**:
- Layered Architecture: Separación clara entre Presentation (Views), Application (Services), Domain (Models) e Infrastructure (Repositories)
- Repository Pattern: Abstracción del acceso a datos con repositorios que encapsulan consultas complejas
- Service Layer Pattern: Lógica de negocio encapsulada en servicios que orquestan operaciones
- RESTful API Design: Recursos como sustantivos, métodos HTTP para acciones, respuestas estructuradas
- Template-based Web UI: Vistas Django con templates HTML para interfaz web

**Reglas y Convenciones**:
- Arquitectura en capas: Views → Services → Repositories → Models (nunca invertir dependencias)
- Nomenclatura: snake_case para funciones, PascalCase para clases, UPPER_SNAKE_CASE para constantes
- Estructura de respuesta uniforme: `{"data": ..., "message": ..., "request": {...}}`
- Manejo de errores con excepciones de DRF (ValidationError, NotFound, PermissionDenied)
- Type hints en todas las funciones públicas
- Validación en serializadores (validación de entrada) y servicios (reglas de negocio)
- Permisos: solo el usuario propietario puede crear, editar y eliminar sus propias sesiones
- Separación de URLs: `api_urls.py` para API REST, `web_urls.py` para vistas web
- Templates Django en `templates/sessions/` siguiendo el patrón de exercises y routines

**Dependencias Técnicas**:
- Django 5.1.7+
- Django REST Framework para API REST
- Django Forms para formularios web
- Relaciones ForeignKey con apps.users, apps.exercises y apps.routines
- No requiere nuevas dependencias externas

**Stack Tecnológico - Capa de Presentación**:
- **Framework/Biblioteca principal**: Django Templates (HTML)
- **Herramientas adicionales**: Django Forms para formularios, mensajes de Django para feedback al usuario
- **Razón de elección**: Mantener consistencia con las apps existentes (users, exercises, routines) que ya utilizan templates Django. Esto permite reutilizar componentes y estilos existentes, mantener un flujo de navegación coherente y aprovechar el sistema de autenticación basado en sesiones de Django.

**Decisiones de Diseño**:
- Sesiones vinculadas opcionalmente a rutinas: ForeignKey con null=True, blank=True
- Ejercicios en sesión: Modelo separado SessionExercise con ForeignKey a Session y Exercise
- Duración calculada automáticamente: Si se proporcionan startTime y endTime, calcular durationMinutes
- RPE: Entero entre 1-10 (validación en serializador/formulario)
- energyLevel: Enum con choices (very_low, low, medium, high, very_high)
- repetitions en SessionExercise: CharField para permitir rangos o arrays (ej: "8-12" o "10,10,9")
- Orden de ejercicios: Campo order en SessionExercise para mantener secuencia
- Permisos: Solo el usuario propietario puede gestionar sus sesiones (ver, crear, editar, eliminar)

## Tareas del Plan de Implementación

### Capa Domain (Modelos)

- [ ] 1. Crear app sessions con estructura básica (__init__.py, apps.py, admin.py, tests.py, factories.py, forms.py)
- [ ] 2. Crear modelo Session en apps/sessions/models.py con todos los campos del dominio (ForeignKey a User y Routine opcional, date, startTime, endTime, durationMinutes, notes, rpe, energyLevel, sleepHours)
- [ ] 3. Crear modelo SessionExercise en apps/sessions/models.py con ForeignKey a Session y Exercise, order, setsCompleted, repetitions, weight, rpe, restSeconds, notes
- [ ] 4. Crear y ejecutar migración para modelos Session y SessionExercise

### Capa Infrastructure (Repositorios)

- [ ] 5. Implementar repositorios en apps/sessions/repositories.py (list_sessions_repository con filtros por usuario y rutina, get_session_by_id_repository, create_session_repository, update_session_repository, delete_session_repository)
- [ ] 6. Implementar repositorios para SessionExercise en apps/sessions/repositories.py (list_session_exercises_repository, get_session_exercise_by_id_repository, create_session_exercise_repository, update_session_exercise_repository, delete_session_exercise_repository)

### Capa Application (Servicios)

- [ ] 7. Implementar servicios en apps/sessions/services.py para Session (list_sessions_service, get_session_service, create_session_service con cálculo de duración, update_session_service, delete_session_service)
- [ ] 8. Implementar servicios en apps/sessions/services.py para SessionExercise (list_session_exercises_service, get_session_exercise_service, create_session_exercise_service, update_session_exercise_service, delete_session_exercise_service)
- [ ] 9. Implementar servicio get_session_full_service que retorna sesión con ejercicios asociados (optimizado con prefetch_related)

### Capa Presentation - API REST (Serializadores y Vistas API)

- [ ] 10. Crear serializadores en apps/sessions/serializers.py (SessionSerializer, SessionCreateSerializer, SessionUpdateSerializer, SessionFullSerializer con ejercicios anidados)
- [ ] 11. Crear serializadores para SessionExercise en apps/sessions/serializers.py (SessionExerciseSerializer, SessionExerciseCreateSerializer, SessionExerciseUpdateSerializer)
- [ ] 12. Implementar vistas API en apps/sessions/views.py (SessionListAPIView, SessionDetailAPIView, SessionCreateAPIView, SessionUpdateAPIView, SessionDeleteAPIView)
- [ ] 13. Implementar vistas API para SessionExercise en apps/sessions/views.py (SessionExerciseListAPIView, SessionExerciseCreateAPIView, SessionExerciseDetailAPIView, SessionExerciseUpdateAPIView, SessionExerciseDeleteAPIView)
- [ ] 14. Crear api_urls.py en apps/sessions/ con rutas para todos los endpoints de sesiones y ejercicios

### Capa Presentation - Web UI (Formularios, Vistas Web y Templates)

- [ ] 15. Crear formularios Django en apps/sessions/forms.py (SessionCreateForm, SessionUpdateForm, SessionExerciseForm)
- [ ] 16. Implementar vistas web en apps/sessions/web_views.py (SessionListView, SessionDetailView, SessionCreateView, SessionUpdateView, SessionDeleteView)
- [ ] 17. Implementar vistas web para SessionExercise en apps/sessions/web_views.py (SessionExerciseCreateView, SessionExerciseUpdateView, SessionExerciseDeleteView)
- [ ] 18. Crear templates Django en apps/sessions/templates/sessions/ (list.html, detail.html, form.html, exercise_form.html)
- [ ] 19. Crear web_urls.py en apps/sessions/ con rutas para todas las vistas web

### Capa Configuration

- [ ] 20. Registrar app sessions en config/settings.py INSTALLED_APPS
- [ ] 21. Añadir rutas api/sessions/ y sessions/ en config/urls.py
- [ ] 22. Registrar modelos Session y SessionExercise en apps/sessions/admin.py con configuración apropiada

### Capa Integración y Navegación

- [ ] 23. Añadir enlaces de navegación desde templates de routines a crear sesión vinculada a rutina
- [ ] 24. Añadir enlaces de navegación desde templates de sessions a ejercicios y rutinas relacionadas
- [ ] 25. Añadir enlaces en templates base/navegación para acceso a sesiones desde menú principal

## Dependencias entre Tareas

- Tarea 2 depende de: 1
- Tarea 3 depende de: 2
- Tarea 4 depende de: 3
- Tarea 5 depende de: 4
- Tarea 6 depende de: 4
- Tarea 7 depende de: 5
- Tarea 8 depende de: 6
- Tarea 9 depende de: 5, 6
- Tarea 10 depende de: 2, 3
- Tarea 11 depende de: 3
- Tarea 12 depende de: 7, 9, 10
- Tarea 13 depende de: 8, 11
- Tarea 14 depende de: 12, 13
- Tarea 15 depende de: 2, 3
- Tarea 16 depende de: 7, 9, 15
- Tarea 17 depende de: 8, 15
- Tarea 18 depende de: 16, 17
- Tarea 19 depende de: 16, 17
- Tarea 20 depende de: 1
- Tarea 21 depende de: 14, 19
- Tarea 22 depende de: 2, 3
- Tarea 23 depende de: 18, 19
- Tarea 24 depende de: 18
- Tarea 25 depende de: 18, 19

## Estimación de Complejidad

- Tarea 1: baja
- Tarea 2: media
- Tarea 3: media
- Tarea 4: baja
- Tarea 5: media
- Tarea 6: media
- Tarea 7: alta
- Tarea 8: alta
- Tarea 9: media
- Tarea 10: alta
- Tarea 11: media
- Tarea 12: alta
- Tarea 13: alta
- Tarea 14: baja
- Tarea 15: media
- Tarea 16: alta
- Tarea 17: alta
- Tarea 18: alta
- Tarea 19: baja
- Tarea 20: baja
- Tarea 21: baja
- Tarea 22: baja
- Tarea 23: baja
- Tarea 24: baja
- Tarea 25: baja

## Riesgos y Mitigaciones

- **Riesgo**: Validación compleja de relaciones entre Session, Routine y User puede causar errores de integridad
  - **Mitigación**: Validar en servicios que el usuario sea propietario de la rutina si se vincula, usar transacciones atómicas para crear sesión con ejercicios

- **Riesgo**: Consultas N+1 al listar sesiones con ejercicios y rutinas asociadas
  - **Mitigación**: Usar select_related('user', 'routine') y prefetch_related('session_exercises__exercise') en queryset del repositorio

- **Riesgo**: Cálculo de duración puede fallar si startTime y endTime no son consistentes
  - **Mitigación**: Validar en servicio que endTime > startTime, calcular durationMinutes automáticamente si ambos están presentes

- **Riesgo**: Permisos mal implementados pueden permitir acceso a sesiones de otros usuarios
  - **Mitigación**: Validar permisos en servicio antes de cualquier operación, verificar que session.user == request.user

- **Riesgo**: Formularios complejos para crear sesión con múltiples ejercicios pueden ser difíciles de usar
  - **Mitigación**: Implementar formulario principal de sesión y formularios separados para añadir ejercicios, usar JavaScript para mejorar UX si es necesario

- **Riesgo**: Integración con rutinas puede requerir lógica compleja para vincular ejercicios de rutina a sesión
  - **Mitigación**: Implementar funcionalidad opcional para "crear sesión desde rutina" que pre-llene ejercicios, pero mantener flexibilidad para sesiones independientes

## Criterios de Aceptación por Tarea

### Tarea 1: Crear app sessions con estructura básica

**Criterios de Aceptación**:
- App sessions creada en apps/sessions/
- Archivos __init__.py, apps.py, admin.py, tests.py, factories.py, forms.py presentes
- apps.py configurado con nombre correcto

### Tarea 2: Crear modelo Session

**Criterios de Aceptación**:
- Modelo Session con todos los campos según DOMAIN.md
- ForeignKey a User con on_delete=CASCADE, related_name="sessions"
- ForeignKey a Routine con null=True, blank=True, related_name="sessions"
- Campos date, startTime, endTime, durationMinutes, notes, rpe, energyLevel, sleepHours
- Choices definidos para energyLevel enum
- Validación de rpe entre 1-10 en clean() o validators
- Índices en campos consultados frecuentemente (user, routine, date)
- Método __str__ implementado
- Meta class con db_table y verbose_name

### Tarea 3: Crear modelo SessionExercise

**Criterios de Aceptación**:
- Modelo SessionExercise con ForeignKey a Session y Exercise
- Campos order, setsCompleted, repetitions, weight, rpe, restSeconds, notes
- Campo order con default=0 y auto-asignación si no se proporciona
- Índices en session y order
- Método __str__ implementado
- Meta class con db_table y verbose_name
- Ordering por order, id

### Tarea 4: Crear y ejecutar migración

**Criterios de Aceptación**:
- Migración creada con makemigrations
- Migración ejecutada con migrate
- Tablas sessions y session_exercises creadas en base de datos
- Campos, relaciones e índices creados correctamente

### Tarea 5: Implementar repositorios para Session

**Criterios de Aceptación**:
- list_sessions_repository con filtros por user (requerido), routine (opcional), date (opcional)
- Ordenamiento por defecto por date descendente (más recientes primero)
- Optimización con select_related('user', 'routine')
- get_session_by_id_repository retorna Session o None
- create_session_repository crea sesión con user
- update_session_repository actualiza campos proporcionados
- delete_session_repository elimina sesión físicamente (o soft delete si se decide)

### Tarea 6: Implementar repositorios para SessionExercise

**Criterios de Aceptación**:
- list_session_exercises_repository con filtro por session, ordenado por order
- Optimización con select_related('exercise')
- get_session_exercise_by_id_repository retorna SessionExercise o None
- create_session_exercise_repository crea ejercicio con auto-asignación de order si no se proporciona
- update_session_exercise_repository actualiza campos proporcionados
- delete_session_exercise_repository elimina ejercicio y reordena si es necesario

### Tarea 7: Implementar servicios para Session

**Criterios de Aceptación**:
- list_sessions_service valida que user sea proporcionado y llama a repositorio
- get_session_service obtiene sesión, verifica permisos (solo propietario), lanza NotFound si no existe
- create_session_service valida datos, calcula durationMinutes si startTime y endTime están presentes, crea sesión
- update_session_service verifica permisos (solo propietario) y actualiza
- delete_session_service verifica permisos (solo propietario) y elimina
- Todas las funciones con type hints

### Tarea 8: Implementar servicios para SessionExercise

**Criterios de Aceptación**:
- list_session_exercises_service valida que session pertenezca al usuario y llama a repositorio
- get_session_exercise_service verifica permisos (sesión pertenece al usuario) y obtiene ejercicio
- create_session_exercise_service verifica permisos, valida datos y crea ejercicio
- update_session_exercise_service verifica permisos y actualiza
- delete_session_exercise_service verifica permisos y elimina
- Todas las funciones con type hints

### Tarea 9: Implementar servicio get_session_full_service

**Criterios de Aceptación**:
- Retorna sesión con ejercicios asociados usando prefetch_related
- Verifica permisos (solo propietario)
- Optimiza consultas para evitar N+1
- Lanza NotFound si sesión no existe

### Tarea 10: Crear serializadores para Session

**Criterios de Aceptación**:
- SessionSerializer (ModelSerializer) con todos los campos
- Campos calculados: user (username o id), routine (name o id)
- Read-only: id, createdAt, updatedAt
- SessionCreateSerializer con validación de campos requeridos (user, date)
- SessionUpdateSerializer con todos los campos opcionales
- SessionFullSerializer con ejercicios anidados usando SessionExerciseSerializer
- Validación de rpe entre 1-10
- Validación de energyLevel enum

### Tarea 11: Crear serializadores para SessionExercise

**Criterios de Aceptación**:
- SessionExerciseSerializer (ModelSerializer) con todos los campos
- Campos calculados: exercise (name o id completo)
- Read-only: id, createdAt, updatedAt
- SessionExerciseCreateSerializer con validación de campos requeridos (session, exercise)
- SessionExerciseUpdateSerializer con todos los campos opcionales
- Validación de rpe entre 1-10 si se proporciona

### Tarea 12: Implementar vistas API para Session

**Criterios de Aceptación**:
- GET /api/sessions/ lista sesiones del usuario autenticado con filtros
- GET /api/sessions/{id}/ obtiene detalle de sesión (solo propietario)
- POST /api/sessions/ crea sesión (IsAuthenticated)
- PUT /api/sessions/{id}/ actualiza sesión (IsAuthenticated, solo propietario)
- DELETE /api/sessions/{id}/ elimina sesión (IsAuthenticated, solo propietario)
- Respuestas estructuradas según patrón del proyecto
- Manejo de errores apropiado con códigos HTTP correctos

### Tarea 13: Implementar vistas API para SessionExercise

**Criterios de Aceptación**:
- GET /api/sessions/{sessionId}/exercises/ lista ejercicios de una sesión (solo propietario de sesión)
- POST /api/sessions/{sessionId}/exercises/ crea ejercicio en sesión (IsAuthenticated, solo propietario de sesión)
- GET /api/sessions/{sessionId}/exercises/{id}/ obtiene detalle de ejercicio (solo propietario de sesión)
- PUT /api/sessions/{sessionId}/exercises/{id}/ actualiza ejercicio (IsAuthenticated, solo propietario de sesión)
- DELETE /api/sessions/{sessionId}/exercises/{id}/ elimina ejercicio (IsAuthenticated, solo propietario de sesión)
- Respuestas estructuradas según patrón del proyecto
- Manejo de errores apropiado

### Tarea 14: Crear api_urls.py

**Criterios de Aceptación**:
- Router o paths configurados para todos los endpoints
- Rutas: sessions/ (lista y crear), sessions/<int:pk>/ (detalle, actualizar, eliminar)
- Rutas anidadas: sessions/<int:sessionId>/exercises/ (lista y crear), sessions/<int:sessionId>/exercises/<int:pk>/ (detalle, actualizar, eliminar)
- Nombres de rutas descriptivos

### Tarea 15: Crear formularios Django

**Criterios de Aceptación**:
- SessionCreateForm con campos: date (requerido), routine (opcional), startTime, endTime, notes, rpe, energyLevel, sleepHours
- SessionUpdateForm con todos los campos opcionales
- SessionExerciseForm con campos: exercise (requerido), order, setsCompleted, repetitions, weight, rpe, restSeconds, notes
- Validación de rpe entre 1-10 en formularios
- Widgets apropiados para campos de fecha/hora

### Tarea 16: Implementar vistas web para Session

**Criterios de Aceptación**:
- SessionListView muestra lista de sesiones del usuario con filtros (por rutina, por fecha)
- SessionDetailView muestra detalle de sesión con ejercicios asociados
- SessionCreateView muestra formulario y procesa creación de sesión
- SessionUpdateView muestra formulario y procesa actualización (solo propietario)
- SessionDeleteView procesa eliminación (solo propietario)
- Todas las vistas requieren login (@login_required)
- Mensajes de éxito/error usando Django messages

### Tarea 17: Implementar vistas web para SessionExercise

**Criterios de Aceptación**:
- SessionExerciseCreateView muestra formulario para añadir ejercicio a sesión
- SessionExerciseUpdateView muestra formulario y procesa actualización
- SessionExerciseDeleteView procesa eliminación
- Todas las vistas verifican que sesión pertenezca al usuario
- Redirección a SessionDetailView después de crear/actualizar/eliminar ejercicio
- Mensajes de éxito/error usando Django messages

### Tarea 18: Crear templates Django

**Criterios de Aceptación**:
- list.html: Lista de sesiones con filtros, enlaces a crear, ver detalle, editar, eliminar
- detail.html: Detalle de sesión con información completa, lista de ejercicios, botones para añadir/editar/eliminar ejercicios, enlace a rutina si está vinculada
- form.html: Formulario para crear/actualizar sesión con todos los campos
- exercise_form.html: Formulario para crear/actualizar ejercicio en sesión
- Templates siguen el patrón de exercises y routines (herencia de base.html, estructura similar)
- Breadcrumbs y navegación coherente

### Tarea 19: Crear web_urls.py

**Criterios de Aceptación**:
- Rutas: sessions/ (lista), sessions/create/ (crear), sessions/<int:pk>/ (detalle), sessions/<int:pk>/update/ (actualizar), sessions/<int:pk>/delete/ (eliminar)
- Rutas anidadas: sessions/<int:pk>/exercises/create/ (crear ejercicio), sessions/<int:pk>/exercises/<int:exerciseId>/update/ (actualizar ejercicio), sessions/<int:pk>/exercises/<int:exerciseId>/delete/ (eliminar ejercicio)
- Nombres de rutas descriptivos

### Tarea 20: Registrar app en settings

**Criterios de Aceptación**:
- apps.sessions añadido a INSTALLED_APPS en config/settings.py

### Tarea 21: Añadir rutas en urls principal

**Criterios de Aceptación**:
- path('api/sessions/', include('apps.sessions.api_urls')) añadido en config/urls.py
- path('sessions/', include('apps.sessions.web_urls')) añadido en config/urls.py

### Tarea 22: Registrar modelos en admin

**Criterios de Aceptación**:
- Session y SessionExercise registrados en admin.py
- list_display configurado con campos relevantes
- list_filter configurado para filtros comunes (user, routine, date)
- search_fields configurado para búsqueda
- Inline admin para SessionExercise dentro de Session

### Tarea 23: Añadir enlaces desde routines

**Criterios de Aceptación**:
- En template routines/detail.html añadir botón "Registrar Sesión" que redirige a sessions/create/ con routine_id pre-seleccionado
- Enlace funcional y visible solo para propietario de rutina

### Tarea 24: Añadir enlaces desde sessions

**Criterios de Aceptación**:
- En template sessions/detail.html añadir enlaces a ejercicio relacionado (si existe en biblioteca)
- En template sessions/detail.html añadir enlace a rutina relacionada (si está vinculada)
- Enlaces funcionales y visibles

### Tarea 25: Añadir enlaces en navegación principal

**Criterios de Aceptación**:
- Añadir enlace "Sesiones" en navegación principal/base.html
- Enlace visible para usuarios autenticados
- Enlace funcional que redirige a sessions/

> Fin del Plan de Implementación para `4_registrar_sesiones_de_entrenamiento`
