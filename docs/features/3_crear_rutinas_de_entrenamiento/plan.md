# Plan de Implementación para Crear Rutinas de Entrenamiento

- **Funcionalidad**: 3_crear_rutinas_de_entrenamiento

Implementar la funcionalidad completa para diseñar y configurar rutinas de entrenamiento personalizadas con estructura jerárquica (Rutina → Semana → Día → Bloque → EjercicioEnRutina) mediante una API REST y una interfaz web con templates Django. El sistema permitirá a los usuarios crear, listar, ver detalles, actualizar y eliminar rutinas completas, así como gestionar su estructura jerárquica (semanas, días, bloques y ejercicios) con navegación integrada a la biblioteca de ejercicios.

## Contexto

### Funcional
- [PRD](/docs/PRD.md)
- [DOMAIN](/docs/DOMAIN.md)
- [Issue #4](https://github.com/jsmdev/thenaturalway-backend/issues/4) - Crear Rutinas de Entrenamiento - Diseñar y configurar rutinas personalizadas

### Técnico

**Patrones Arquitectónicos**:
- Layered Architecture: Separación clara entre Presentation (Views/WebViews), Application (Services), Domain (Models) e Infrastructure (Repositories)
- Repository Pattern: Abstracción del acceso a datos con repositorios que encapsulan consultas complejas
- Service Layer Pattern: Lógica de negocio encapsulada en servicios que orquestan operaciones
- RESTful API Design: Recursos como sustantivos, métodos HTTP para acciones, respuestas estructuradas
- Hierarchical Data Management: Gestión de estructuras jerárquicas anidadas (Rutina → Semana → Día → Bloque → EjercicioEnRutina)

**Reglas y Convenciones**:
- Arquitectura en capas: Views → Services → Repositories → Models (nunca invertir dependencias)
- Nomenclatura: snake_case para funciones, PascalCase para clases, UPPER_SNAKE_CASE para constantes
- Estructura de respuesta uniforme: `{"data": ..., "message": ..., "request": {...}}`
- Manejo de errores con excepciones de DRF (ValidationError, NotFound, PermissionDenied)
- Type hints en todas las funciones públicas
- Validación en serializadores (validación de entrada) y servicios (reglas de negocio)
- Soft delete mediante `isActive=False` (no eliminación física)
- Permisos: solo el creador puede editar/eliminar sus rutinas
- Navegación integrada: enlaces entre rutinas y ejercicios en la interfaz web

**Dependencias Técnicas**:
- Django 5.1.7+
- Django REST Framework para API REST
- Django Forms para formularios web
- Templates Django para interfaz web
- Relación con app exercises (ForeignKey a Exercise)
- Relación con app users (ForeignKey a User)

**Stack Tecnológico - Capa de Presentación**:
- **Framework/Biblioteca principal**: Django Templates (HTML + CSS inline en base.html)
- **Herramientas adicionales**: Django Forms para formularios, mensajes de Django para feedback al usuario
- **Razón de elección**: Mantener consistencia con las apps existentes (users y exercises) que ya usan templates Django. El proyecto ya tiene base.html configurado con estilos CSS inline, por lo que se mantendrá el mismo stack para uniformidad visual y de desarrollo.

**Decisiones de Diseño**:
- Soft delete: Marcar `isActive=False` (no campo `deleted_at`)
- Estructura jerárquica: Rutina → Semana → Día → Bloque → EjercicioEnRutina (cascada de eliminación)
- Endpoints anidados: `/api/routines/{id}/weeks/`, `/api/routines/{id}/weeks/{weekId}/days/`, etc.
- Navegación web: Vista de detalle de rutina con estructura expandible/colapsable para semanas, días, bloques y ejercicios
- Integración con ejercicios: Selector de ejercicios desde la biblioteca al añadir EjercicioEnRutina
- Ordenamiento: Campos `order` en Bloque y EjercicioEnRutina para mantener secuencia
- Validación: Verificar que ejercicios existan antes de añadirlos a rutinas

## Tareas del Plan de Implementación

### Capa Domain (Modelos)

- [ ] 1. Crear app routines con estructura básica (__init__.py, apps.py, admin.py, tests.py, forms.py, web_views.py, api_urls.py, web_urls.py)
- [ ] 2. Crear modelo Routine en apps/routines/models.py con todos los campos del dominio (name, description, durationWeeks, durationMonths, isActive, createdBy)
- [ ] 3. Crear modelo Week en apps/routines/models.py con relación a Routine (routineId, weekNumber, notes)
- [ ] 4. Crear modelo Day en apps/routines/models.py con relación a Week (weekId, dayNumber, name, notes)
- [ ] 5. Crear modelo Block en apps/routines/models.py con relación a Day (dayId, name, order, notes)
- [ ] 6. Crear modelo RoutineExercise en apps/routines/models.py con relación a Block y Exercise (blockId, exerciseId, order, sets, repetitions, weight, weightPercentage, tempo, restSeconds, notes)
- [ ] 7. Crear y ejecutar migraciones para todos los modelos

### Capa Infrastructure (Repositorios)

- [ ] 8. Implementar repositorios en apps/routines/repositories.py para Routine (list, get, create, update, delete con filtros por usuario)
- [ ] 9. Implementar repositorios para Week (list_by_routine, get, create, update, delete)
- [ ] 10. Implementar repositorios para Day (list_by_week, get, create, update, delete)
- [ ] 11. Implementar repositorios para Block (list_by_day, get, create, update, delete)
- [ ] 12. Implementar repositorios para RoutineExercise (list_by_block, get, create, update, delete)
- [ ] 13. Implementar repositorio get_routine_full_repository para obtener rutina completa con toda su jerarquía (optimizado con select_related y prefetch_related)

### Capa Application (Servicios)

- [ ] 14. Implementar servicios en apps/routines/services.py para Routine (list, get, create, update, delete con validaciones y permisos)
- [ ] 15. Implementar servicios para Week (create, update, delete con validación de pertenencia a rutina)
- [ ] 16. Implementar servicios para Day (create, update, delete con validación de pertenencia a semana)
- [ ] 17. Implementar servicios para Block (create, update, delete con validación de pertenencia a día y reordenamiento)
- [ ] 18. Implementar servicios para RoutineExercise (create, update, delete con validación de ejercicio existente y reordenamiento)
- [ ] 19. Implementar servicio get_routine_full_service para obtener rutina completa con jerarquía

### Capa Presentation - API (Serializadores y Vistas)

- [ ] 20. Crear serializadores en apps/routines/serializers.py (RoutineSerializer, RoutineCreateSerializer, RoutineUpdateSerializer, RoutineFullSerializer con jerarquía anidada)
- [ ] 21. Crear serializadores para Week, Day, Block, RoutineExercise (serializadores base y de creación)
- [ ] 22. Implementar vistas API en apps/routines/views.py (RoutineListAPIView, RoutineDetailAPIView con endpoints CRUD)
- [ ] 23. Implementar vistas API anidadas (WeekCreateAPIView, DayCreateAPIView, BlockCreateAPIView, RoutineExerciseCreateAPIView)
- [ ] 24. Crear api_urls.py en apps/routines/ con rutas para todos los endpoints API

### Capa Presentation - Web (Formularios, Vistas y Templates)

- [ ] 25. Crear formularios Django en apps/routines/forms.py (RoutineCreateForm, RoutineUpdateForm, WeekForm, DayForm, BlockForm, RoutineExerciseForm)
- [ ] 26. Implementar vistas web en apps/routines/web_views.py (RoutineListView, RoutineDetailView, RoutineCreateView, RoutineUpdateView, RoutineDeleteView)
- [ ] 27. Implementar vistas web anidadas (WeekCreateView, DayCreateView, BlockCreateView, RoutineExerciseCreateView)
- [ ] 28. Crear template list.html en apps/routines/templates/routines/ para listar rutinas del usuario
- [ ] 29. Crear template detail.html en apps/routines/templates/routines/ para mostrar rutina completa con estructura jerárquica expandible/colapsable
- [ ] 30. Crear template form.html en apps/routines/templates/routines/ para crear/editar rutina
- [ ] 31. Crear templates parciales para componentes (week_section.html, day_section.html, block_section.html, exercise_item.html)
- [ ] 32. Crear web_urls.py en apps/routines/ con rutas para todas las vistas web

### Capa Configuration e Integración

- [ ] 33. Registrar app routines en config/settings.py INSTALLED_APPS
- [ ] 34. Añadir rutas API (api/routines/) y web (routines/) en config/urls.py
- [ ] 35. Registrar todos los modelos en apps/routines/admin.py con configuración apropiada
- [ ] 36. Actualizar templates/base.html para incluir enlace de navegación a rutinas en el menú
- [ ] 37. Añadir enlaces de navegación en templates de exercises para crear rutina desde ejercicio
- [ ] 38. Añadir enlaces de navegación en templates de routines para ver ejercicios de la biblioteca

## Dependencias entre Tareas

- Tarea 2 depende de: 1
- Tarea 3 depende de: 2
- Tarea 4 depende de: 3
- Tarea 5 depende de: 4
- Tarea 6 depende de: 5 (y requiere que exista modelo Exercise)
- Tarea 7 depende de: 6
- Tarea 8 depende de: 2
- Tarea 9 depende de: 3, 8
- Tarea 10 depende de: 4, 9
- Tarea 11 depende de: 5, 10
- Tarea 12 depende de: 6, 11
- Tarea 13 depende de: 8, 9, 10, 11, 12
- Tarea 14 depende de: 8
- Tarea 15 depende de: 9, 14
- Tarea 16 depende de: 10, 15
- Tarea 17 depende de: 11, 16
- Tarea 18 depende de: 12, 17
- Tarea 19 depende de: 13, 14
- Tarea 20 depende de: 2, 3, 4, 5, 6
- Tarea 21 depende de: 3, 4, 5, 6
- Tarea 22 depende de: 14, 20
- Tarea 23 depende de: 15, 16, 17, 18, 21
- Tarea 24 depende de: 22, 23
- Tarea 25 depende de: 2, 3, 4, 5, 6
- Tarea 26 depende de: 14, 25
- Tarea 27 depende de: 15, 16, 17, 18, 25
- Tarea 28 depende de: 26
- Tarea 29 depende de: 19, 26
- Tarea 30 depende de: 26
- Tarea 31 depende de: 29
- Tarea 32 depende de: 26, 27
- Tarea 33 depende de: 1
- Tarea 34 depende de: 24, 32
- Tarea 35 depende de: 2, 3, 4, 5, 6
- Tarea 36 depende de: 32
- Tarea 37 depende de: 32
- Tarea 38 depende de: 32

## Estimación de Complejidad

- Tarea 1: baja
- Tarea 2: media
- Tarea 3: baja
- Tarea 4: baja
- Tarea 5: baja
- Tarea 6: media
- Tarea 7: baja
- Tarea 8: media
- Tarea 9: baja
- Tarea 10: baja
- Tarea 11: baja
- Tarea 12: media
- Tarea 13: alta
- Tarea 14: media
- Tarea 15: media
- Tarea 16: media
- Tarea 17: media
- Tarea 18: media
- Tarea 19: alta
- Tarea 20: alta
- Tarea 21: media
- Tarea 22: alta
- Tarea 23: alta
- Tarea 24: baja
- Tarea 25: media
- Tarea 26: alta
- Tarea 27: alta
- Tarea 28: media
- Tarea 29: alta
- Tarea 30: media
- Tarea 31: media
- Tarea 32: baja
- Tarea 33: baja
- Tarea 34: baja
- Tarea 35: baja
- Tarea 36: baja
- Tarea 37: baja
- Tarea 38: baja

## Riesgos y Mitigaciones

- **Riesgo**: Consultas N+1 al obtener rutina completa con toda su jerarquía
  - **Mitigación**: Usar select_related y prefetch_related anidados en get_routine_full_repository, optimizar querysets con prefetch_related('days__blocks__routine_exercises__exercise')

- **Riesgo**: Validación compleja de estructura jerárquica puede causar errores
  - **Mitigación**: Validar en servicios que Week pertenece a Routine, Day pertenece a Week, etc. antes de crear/actualizar/eliminar

- **Riesgo**: Permisos mal implementados pueden permitir edición/eliminación por usuarios no autorizados
  - **Mitigación**: Validar permisos en servicio antes de actualizar/eliminar, verificar que createdBy == user en todos los niveles

- **Riesgo**: Reordenamiento de bloques y ejercicios puede ser complejo
  - **Mitigación**: Implementar lógica de reordenamiento en servicios que actualice campos `order` de forma atómica

- **Riesgo**: Templates complejos con estructura jerárquica pueden ser difíciles de mantener
  - **Mitigación**: Usar templates parciales (includes) para cada nivel de la jerarquía, mantener estructura modular

- **Riesgo**: Integración con app exercises puede fallar si ejercicio no existe
  - **Mitigación**: Validar en servicio que exerciseId existe antes de crear RoutineExercise, manejar NotFound apropiadamente

## Criterios de Aceptación por Tarea

### Tarea 1: Crear app routines con estructura básica

**Criterios de Aceptación**:
- App routines creada en apps/routines/
- Archivos __init__.py, apps.py, admin.py, tests.py, forms.py, web_views.py, api_urls.py, web_urls.py presentes
- apps.py configurado con nombre correcto

### Tarea 2: Crear modelo Routine

**Criterios de Aceptación**:
- Modelo Routine con todos los campos según DOMAIN.md (name, description, durationWeeks, durationMonths, isActive, createdBy)
- ForeignKey a User con on_delete apropiado
- Índices en campos consultados frecuentemente (createdBy, isActive)
- Método __str__ implementado
- Meta class con db_table y verbose_name

### Tarea 3: Crear modelo Week

**Criterios de Aceptación**:
- Modelo Week con campos routineId, weekNumber, notes
- ForeignKey a Routine con on_delete=CASCADE
- Validación de weekNumber único por rutina
- Método __str__ implementado

### Tarea 4: Crear modelo Day

**Criterios de Aceptación**:
- Modelo Day con campos weekId, dayNumber, name, notes
- ForeignKey a Week con on_delete=CASCADE
- Validación de dayNumber único por semana
- Método __str__ implementado

### Tarea 5: Crear modelo Block

**Criterios de Aceptación**:
- Modelo Block con campos dayId, name, order, notes
- ForeignKey a Day con on_delete=CASCADE
- Campo order para mantener secuencia
- Método __str__ implementado

### Tarea 6: Crear modelo RoutineExercise

**Criterios de Aceptación**:
- Modelo RoutineExercise con todos los campos según DOMAIN.md
- ForeignKey a Block con on_delete=CASCADE
- ForeignKey a Exercise (de app exercises) con validación
- Campo order para mantener secuencia
- Campos opcionales para sets, repetitions, weight, weightPercentage, tempo, restSeconds, notes
- Método __str__ implementado

### Tarea 7: Crear y ejecutar migraciones

**Criterios de Aceptación**:
- Migraciones creadas con makemigrations
- Migraciones ejecutadas con migrate
- Todas las tablas creadas en base de datos
- Relaciones ForeignKey y restricciones creadas correctamente

### Tarea 8: Implementar repositorios para Routine

**Criterios de Aceptación**:
- list_routines_repository filtra por usuario creador
- get_routine_by_id_repository retorna Routine o None
- create_routine_repository crea rutina con createdBy
- update_routine_repository actualiza campos proporcionados
- delete_routine_repository realiza soft delete (isActive=False)
- Optimización con select_related('createdBy')

### Tarea 9: Implementar repositorios para Week

**Criterios de Aceptación**:
- list_weeks_by_routine_repository lista semanas de una rutina ordenadas por weekNumber
- get_week_by_id_repository retorna Week o None
- create_week_repository crea semana con validación de weekNumber único
- update_week_repository actualiza campos
- delete_week_repository elimina semana (CASCADE eliminará días, bloques y ejercicios)

### Tarea 10: Implementar repositorios para Day

**Criterios de Aceptación**:
- list_days_by_week_repository lista días de una semana ordenados por dayNumber
- get_day_by_id_repository retorna Day o None
- create_day_repository crea día con validación de dayNumber único
- update_day_repository actualiza campos
- delete_day_repository elimina día (CASCADE eliminará bloques y ejercicios)

### Tarea 11: Implementar repositorios para Block

**Criterios de Aceptación**:
- list_blocks_by_day_repository lista bloques de un día ordenados por order
- get_block_by_id_repository retorna Block o None
- create_block_repository crea bloque con order automático
- update_block_repository actualiza campos y puede reordenar
- delete_block_repository elimina bloque (CASCADE eliminará ejercicios)

### Tarea 12: Implementar repositorios para RoutineExercise

**Criterios de Aceptación**:
- list_routine_exercises_by_block_repository lista ejercicios de un bloque ordenados por order
- get_routine_exercise_by_id_repository retorna RoutineExercise o None
- create_routine_exercise_repository crea ejercicio con order automático
- update_routine_exercise_repository actualiza campos y puede reordenar
- delete_routine_exercise_repository elimina ejercicio

### Tarea 13: Implementar repositorio get_routine_full_repository

**Criterios de Aceptación**:
- Obtiene rutina con toda su jerarquía (semanas, días, bloques, ejercicios)
- Optimización con select_related y prefetch_related anidados
- Retorna estructura de datos optimizada para serialización
- Maneja casos donde rutina no tiene semanas/días/bloques/ejercicios

### Tarea 14: Implementar servicios para Routine

**Criterios de Aceptación**:
- list_routines_service filtra por usuario autenticado
- get_routine_service obtiene rutina, lanza NotFound si no existe o no pertenece al usuario
- create_routine_service valida datos y crea rutina
- update_routine_service verifica permisos (solo creador) y actualiza
- delete_routine_service verifica permisos (solo creador) y realiza soft delete
- Todas las funciones con type hints

### Tarea 15: Implementar servicios para Week

**Criterios de Aceptación**:
- create_week_service valida que rutina pertenece al usuario y crea semana
- update_week_service verifica permisos y actualiza
- delete_week_service verifica permisos y elimina
- Validación de weekNumber único por rutina

### Tarea 16: Implementar servicios para Day

**Criterios de Aceptación**:
- create_day_service valida que semana pertenece a rutina del usuario y crea día
- update_day_service verifica permisos y actualiza
- delete_day_service verifica permisos y elimina
- Validación de dayNumber único por semana

### Tarea 17: Implementar servicios para Block

**Criterios de Aceptación**:
- create_block_service valida que día pertenece a rutina del usuario y crea bloque
- update_block_service verifica permisos, actualiza y puede reordenar
- delete_block_service verifica permisos y elimina
- Lógica de reordenamiento automático de order

### Tarea 18: Implementar servicios para RoutineExercise

**Criterios de Aceptación**:
- create_routine_exercise_service valida que bloque pertenece a rutina del usuario, verifica que ejercicio existe y crea
- update_routine_exercise_service verifica permisos, actualiza y puede reordenar
- delete_routine_exercise_service verifica permisos y elimina
- Validación de que exerciseId existe en app exercises
- Lógica de reordenamiento automático de order

### Tarea 19: Implementar servicio get_routine_full_service

**Criterios de Aceptación**:
- Obtiene rutina completa con jerarquía usando repositorio optimizado
- Verifica permisos (solo creador puede ver)
- Retorna estructura de datos lista para serialización
- Maneja errores apropiadamente

### Tarea 20: Crear serializadores para Routine

**Criterios de Aceptación**:
- RoutineSerializer (ModelSerializer) con todos los campos
- RoutineCreateSerializer con validación de campos requeridos
- RoutineUpdateSerializer con todos los campos opcionales
- RoutineFullSerializer con jerarquía anidada (semanas → días → bloques → ejercicios)
- Campos calculados: createdBy (username o id)
- Read-only: id, createdAt, updatedAt

### Tarea 21: Crear serializadores para Week, Day, Block, RoutineExercise

**Criterios de Aceptación**:
- Serializadores base para cada modelo (WeekSerializer, DaySerializer, BlockSerializer, RoutineExerciseSerializer)
- Serializadores de creación para cada modelo
- RoutineExerciseSerializer incluye información del Exercise relacionado
- Validación de campos requeridos y opcionales

### Tarea 22: Implementar vistas API para Routine

**Criterios de Aceptación**:
- GET /api/routines/ lista rutinas del usuario autenticado
- GET /api/routines/{id}/ obtiene detalle de rutina (con opción de incluir jerarquía completa)
- POST /api/routines/ crea rutina (IsAuthenticated)
- PUT /api/routines/{id}/ actualiza rutina (IsAuthenticated, solo creador)
- DELETE /api/routines/{id}/ elimina rutina (IsAuthenticated, solo creador)
- Respuestas estructuradas según patrón del proyecto
- Manejo de errores apropiado con códigos HTTP correctos

### Tarea 23: Implementar vistas API anidadas

**Criterios de Aceptación**:
- POST /api/routines/{id}/weeks/ crea semana en rutina
- POST /api/routines/{id}/weeks/{weekId}/days/ crea día en semana
- POST /api/routines/{id}/days/{dayId}/blocks/ crea bloque en día
- POST /api/routines/{id}/blocks/{blockId}/exercises/ crea ejercicio en bloque
- Todas las vistas verifican permisos y pertenencia
- Respuestas estructuradas con datos creados

### Tarea 24: Crear api_urls.py

**Criterios de Aceptación**:
- Paths configurados para todos los endpoints API
- Rutas: routines/ (lista y crear), routines/<int:pk>/ (detalle, actualizar, eliminar)
- Rutas anidadas: routines/<int:pk>/weeks/, routines/<int:pk>/weeks/<int:weekId>/days/, etc.
- Nombres de rutas descriptivos

### Tarea 25: Crear formularios Django

**Criterios de Aceptación**:
- RoutineCreateForm con campos name, description, durationWeeks, durationMonths
- RoutineUpdateForm con todos los campos opcionales
- WeekForm para crear/editar semanas
- DayForm para crear/editar días
- BlockForm para crear/editar bloques
- RoutineExerciseForm con selector de ejercicios (ChoiceField con ejercicios de la biblioteca)
- Validación de campos requeridos y formatos

### Tarea 26: Implementar vistas web para Routine

**Criterios de Aceptación**:
- RoutineListView lista rutinas del usuario con filtros
- RoutineDetailView muestra rutina completa con estructura jerárquica
- RoutineCreateView muestra formulario y crea rutina
- RoutineUpdateView muestra formulario y actualiza rutina
- RoutineDeleteView elimina rutina (soft delete)
- Todas las vistas requieren autenticación
- Verificación de permisos (solo creador puede editar/eliminar)
- Mensajes de éxito/error usando Django messages

### Tarea 27: Implementar vistas web anidadas

**Criterios de Aceptación**:
- WeekCreateView crea semana desde vista de detalle de rutina
- DayCreateView crea día desde vista de detalle de semana
- BlockCreateView crea bloque desde vista de detalle de día
- RoutineExerciseCreateView crea ejercicio en bloque con selector de ejercicios
- Todas las vistas verifican permisos y pertenencia
- Redirección apropiada después de crear

### Tarea 28: Crear template list.html

**Criterios de Aceptación**:
- Template que lista rutinas del usuario
- Muestra nombre, descripción, duración, estado activo
- Enlaces a crear nueva rutina, ver detalle, editar, eliminar
- Filtros y búsqueda (opcional)
- Extiende base.html
- Estilos consistentes con templates existentes

### Tarea 29: Crear template detail.html

**Criterios de Aceptación**:
- Template que muestra rutina completa con estructura jerárquica
- Secciones expandibles/colapsables para semanas, días, bloques
- Muestra información completa de cada nivel
- Enlaces para añadir semanas, días, bloques, ejercicios
- Enlaces para editar/eliminar cada elemento
- Integración con ejercicios: muestra nombre del ejercicio y enlace a detalle
- Extiende base.html
- JavaScript para expandir/colapsar secciones (opcional)

### Tarea 30: Crear template form.html

**Criterios de Aceptación**:
- Template para crear/editar rutina
- Formulario con todos los campos de Routine
- Validación de campos requeridos
- Mensajes de error de formulario
- Botones para guardar y cancelar
- Extiende base.html
- Estilos consistentes con templates existentes

### Tarea 31: Crear templates parciales

**Criterios de Aceptación**:
- week_section.html: Muestra sección de semana con días
- day_section.html: Muestra sección de día con bloques
- block_section.html: Muestra sección de bloque con ejercicios
- exercise_item.html: Muestra item de ejercicio en rutina
- Templates reutilizables usando {% include %}
- Estilos consistentes

### Tarea 32: Crear web_urls.py

**Criterios de Aceptación**:
- Paths configurados para todas las vistas web
- Rutas: routines/ (lista), routines/<int:pk>/ (detalle), routines/create/ (crear), routines/<int:pk>/update/ (editar), routines/<int:pk>/delete/ (eliminar)
- Rutas anidadas: routines/<int:pk>/weeks/create/, routines/<int:pk>/weeks/<int:weekId>/days/create/, etc.
- Nombres de rutas descriptivos

### Tarea 33: Registrar app en settings

**Criterios de Aceptación**:
- apps.routines añadido a INSTALLED_APPS en config/settings.py

### Tarea 34: Añadir rutas en urls principal

**Criterios de Aceptación**:
- path('api/routines/', include('apps.routines.api_urls')) añadido en config/urls.py
- path('routines/', include('apps.routines.web_urls')) añadido en config/urls.py

### Tarea 35: Registrar modelos en admin

**Criterios de Aceptación**:
- Todos los modelos registrados en admin.py (Routine, Week, Day, Block, RoutineExercise)
- list_display configurado con campos relevantes
- list_filter configurado para filtros comunes
- search_fields configurado para búsqueda
- Inline admin para jerarquía (opcional)

### Tarea 36: Actualizar base.html para navegación

**Criterios de Aceptación**:
- Enlace "Rutinas" añadido al menú de navegación en base.html
- Enlace visible para usuarios autenticados
- Estilos consistentes con enlaces existentes

### Tarea 37: Añadir enlaces en templates de exercises

**Criterios de Aceptación**:
- Enlace "Crear rutina con este ejercicio" en detail.html de exercises
- Enlace opcional en list.html de exercises
- Navegación fluida entre apps

### Tarea 38: Añadir enlaces en templates de routines

**Criterios de Aceptación**:
- Enlace "Ver biblioteca de ejercicios" en templates de routines
- Enlace a detalle de ejercicio desde RoutineExercise en detail.html
- Navegación fluida entre apps

> Fin del Plan de Implementación para `3_crear_rutinas_de_entrenamiento`

