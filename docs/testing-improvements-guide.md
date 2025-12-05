# Guía de Mejoras para Tests - The Natural Way Backend

## Resumen Ejecutivo

Este documento proporciona instrucciones detalladas para aplicar mejoras a los tests de las tres apps principales del proyecto: `users`, `exercises` y `routines`. Las mejoras están diseñadas para ser implementadas por una IA de forma sistemática y consistente.

## Estado Actual

### Aspectos Positivos ✅
- **Estructura clara**: Tests organizados por capas (Modelos, Repositorios, Servicios, Serializadores, Vistas)
- **Patrón AAA**: Arrange-Act-Assert bien aplicado
- **Nombres descriptivos**: Los nombres de tests explican claramente qué se está probando
- **Cobertura amplia**: Tests para casos exitosos, errores, permisos y validaciones
- **Type hints**: Uso consistente de type hints

### Áreas de Mejora Identificadas 📈
1. Inconsistencia en el uso de mocks en tests de servicios
2. Cobertura incompleta de servicios (faltan tests de update/delete)
3. Falta de factory pattern para simplificar creación de objetos de prueba
4. URLs hardcodeadas en tests de API
5. Uso ineficiente de `setUp()` vs `setUpTestData()`
6. Tests de repositorios solo cubren casos exitosos
7. Faltan tests de integración end-to-end

---

## Mejora 1: Implementar Factory Pattern con Factory Boy

### Objetivo
Simplificar la creación de objetos de prueba y eliminar código repetitivo en los `setUp()` de cada test.

### Instrucciones de Implementación

#### Paso 1.1: Instalar Factory Boy

Agregar al archivo `requirements.txt`:

```
factory-boy==3.3.0
```

#### Paso 1.2: Crear archivo de factories

**Ubicación**: `/apps/users/factories.py`

```python
from __future__ import annotations

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory para crear usuarios de prueba."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
```

**Ubicación**: `/apps/exercises/factories.py`

```python
from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from apps.exercises.models import Exercise
from apps.users.factories import UserFactory


class ExerciseFactory(DjangoModelFactory):
    """Factory para crear ejercicios de prueba."""

    class Meta:
        model = Exercise

    name = factory.Sequence(lambda n: f"Exercise {n}")
    description = factory.Faker("text", max_nb_chars=200)
    movement_type = factory.Iterator(["push", "pull", "legs", "core", "cardio"])
    primary_muscle_group = factory.Iterator(
        ["chest", "back", "shoulders", "arms", "legs", "core", "full_body"]
    )
    equipment = factory.Iterator(
        ["barbell", "dumbbell", "bodyweight", "machine", "cable", "other"]
    )
    difficulty = factory.Iterator(["beginner", "intermediate", "advanced"])
    is_active = True
    created_by = factory.SubFactory(UserFactory)
```

**Ubicación**: `/apps/routines/factories.py`

```python
from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from apps.routines.models import Routine, Week, Day, Block, RoutineExercise
from apps.users.factories import UserFactory
from apps.exercises.factories import ExerciseFactory


class RoutineFactory(DjangoModelFactory):
    """Factory para crear rutinas de prueba."""

    class Meta:
        model = Routine

    name = factory.Sequence(lambda n: f"Routine {n}")
    description = factory.Faker("text", max_nb_chars=200)
    duration_weeks = factory.Faker("random_int", min=4, max=24)
    is_active = True
    created_by = factory.SubFactory(UserFactory)


class WeekFactory(DjangoModelFactory):
    """Factory para crear semanas de prueba."""

    class Meta:
        model = Week

    routine = factory.SubFactory(RoutineFactory)
    week_number = factory.Sequence(lambda n: n + 1)
    notes = factory.Faker("text", max_nb_chars=100)


class DayFactory(DjangoModelFactory):
    """Factory para crear días de prueba."""

    class Meta:
        model = Day

    week = factory.SubFactory(WeekFactory)
    day_number = factory.Sequence(lambda n: (n % 7) + 1)
    name = factory.LazyAttribute(lambda obj: f"Day {obj.day_number}")
    notes = factory.Faker("text", max_nb_chars=100)


class BlockFactory(DjangoModelFactory):
    """Factory para crear bloques de prueba."""

    class Meta:
        model = Block

    day = factory.SubFactory(DayFactory)
    name = factory.Sequence(lambda n: f"Block {n}")
    order = factory.Sequence(lambda n: n + 1)
    notes = factory.Faker("text", max_nb_chars=100)


class RoutineExerciseFactory(DjangoModelFactory):
    """Factory para crear ejercicios en rutina de prueba."""

    class Meta:
        model = RoutineExercise

    block = factory.SubFactory(BlockFactory)
    exercise = factory.SubFactory(ExerciseFactory)
    order = factory.Sequence(lambda n: n + 1)
    sets = factory.Faker("random_int", min=1, max=5)
    repetitions = factory.Iterator(["8-10", "10-12", "12-15", "15-20"])
    weight = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    rest_seconds = factory.Iterator([30, 60, 90, 120])
```

#### Paso 1.3: Ejemplo de uso de factories en tests

**Antes (sin factories)**:
```python
def setUp(self) -> None:
    self.user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    self.exercise = Exercise.objects.create(
        name="Push Up",
        primary_muscle_group="chest",
        created_by=self.user
    )
```

**Después (con factories)**:
```python
def setUp(self) -> None:
    self.user = UserFactory()
    self.exercise = ExerciseFactory(created_by=self.user)
```

---

## Mejora 2: Usar `setUpTestData()` en lugar de `setUp()`

### Objetivo
Mejorar el rendimiento de los tests creando datos una sola vez por clase de test en lugar de recrearlos para cada test individual.

### Instrucciones de Implementación

#### Regla General
- Usar `setUpTestData()` para datos que **no se modifican** durante los tests
- Usar `setUp()` solo para datos que **sí se modifican** en los tests

#### Ejemplo de Implementación

**Antes**:
```python
class ExerciseModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_exercise_creation(self):
        exercise = Exercise.objects.create(name="Test", created_by=self.user)
        # ...
```

**Después**:
```python
class ExerciseModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Crea datos una sola vez para toda la clase de test."""
        cls.user = UserFactory()

    def test_exercise_creation(self):
        exercise = Exercise.objects.create(name="Test", created_by=self.user)
        # ...
```

---

## Mejora 3: Corregir Uso de Mocks en Tests de Servicios

### Objetivo
Asegurar que los tests de servicios no creen objetos reales en la base de datos cuando todos los repositorios están mockeados.

### Instrucciones de Implementación

#### Problema Identificado
En los tests de servicios, se crean objetos reales con `Model.objects.create()` cuando deberían usarse solo mocks.

**Incorrecto** (crea objeto real en BD):
```python
@patch("apps.routines.services.list_routines_repository")
def test_list_routines_service_success(self, mock_repo: MagicMock) -> None:
    # ❌ Esto crea un objeto real en la BD
    routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
    mock_repo.return_value = [routine]
```

**Correcto** (usa solo mock):
```python
@patch("apps.routines.services.list_routines_repository")
def test_list_routines_service_success(self, mock_repo: MagicMock) -> None:
    # ✅ Esto crea un objeto mock sin guardar en BD
    routine = Routine(name="Rutina Test", created_by=self.user)
    routine.id = 1  # Simular que tiene ID
    mock_repo.return_value = [routine]
```

#### Archivos a Modificar

**App: `routines`**
- Archivo: `apps/routines/tests.py`
- Tests a corregir:
  - `RoutineServiceTestCase.test_list_routines_service_success` (línea 1083)
  - `RoutineServiceTestCase.test_get_routine_service_success` (línea 1098)
  - `RoutineServiceTestCase.test_create_routine_service_success` (línea 1142)
  - `RoutineServiceTestCase.test_update_routine_service_success` (líneas 1173-1176)
  - `RoutineServiceTestCase.test_delete_routine_service_success` (líneas 1228-1230)
  - `BlockServiceTestCase.test_create_block_service_success` (línea 1445)
  - `RoutineExerciseServiceTestCase.test_create_routine_exercise_service_success` (línea 1490)

**App: `exercises`**
- Archivo: `apps/exercises/tests.py`
- Tests a corregir:
  - `ExerciseServiceTestCase.test_create_exercise_service_success` (línea 558)
  - `ExerciseServiceTestCase.test_update_exercise_service_success` (línea 613)
  - `ExerciseServiceTestCase.test_delete_exercise_service_success` (línea 663)

#### Patrón de Corrección

Para cada test identificado, aplicar la siguiente transformación:

```python
# ANTES
routine = Routine.objects.create(name="Test", created_by=self.user)
mock_repo.return_value = routine

# DESPUÉS
routine = Routine(name="Test", created_by=self.user)
routine.id = 1  # Simular ID sin guardar en BD
mock_repo.return_value = routine
```

---

## Mejora 4: Agregar Tests Faltantes para Servicios

### Objetivo
Completar la cobertura de tests para todos los servicios CRUD (Create, Read, Update, Delete).

### Tests Faltantes Identificados

#### App: `routines`

**Servicios sin tests de Update**:
1. `update_week_service` - agregar tests:
   - ✅ Ya existe `test_update_week_service_success`
   - ❌ Falta `test_update_week_service_not_found`
   - ❌ Falta `test_update_week_service_permission_denied`

2. `update_day_service` - agregar todos los tests:
   - ❌ `test_update_day_service_success`
   - ❌ `test_update_day_service_not_found`
   - ❌ `test_update_day_service_permission_denied`
   - ❌ `test_update_day_service_duplicate_day_number`

3. `update_block_service` - agregar todos los tests:
   - ❌ `test_update_block_service_success`
   - ❌ `test_update_block_service_not_found`
   - ❌ `test_update_block_service_permission_denied`

4. `update_routine_exercise_service` - agregar todos los tests:
   - ❌ `test_update_routine_exercise_service_success`
   - ❌ `test_update_routine_exercise_service_not_found`
   - ❌ `test_update_routine_exercise_service_permission_denied`

**Servicios sin tests de Delete**:
1. `delete_week_service` - solo tiene 1 test success, agregar:
   - ❌ `test_delete_week_service_not_found`
   - ❌ `test_delete_week_service_permission_denied`

2. `delete_day_service` - agregar todos los tests:
   - ❌ `test_delete_day_service_success`
   - ❌ `test_delete_day_service_not_found`
   - ❌ `test_delete_day_service_permission_denied`

3. `delete_block_service` - agregar todos los tests:
   - ❌ `test_delete_block_service_success`
   - ❌ `test_delete_block_service_not_found`
   - ❌ `test_delete_block_service_permission_denied`

4. `delete_routine_exercise_service` - agregar todos los tests:
   - ❌ `test_delete_routine_exercise_service_success`
   - ❌ `test_delete_routine_exercise_service_not_found`
   - ❌ `test_delete_routine_exercise_service_permission_denied`

#### Template de Test para Update Service

```python
@patch("apps.routines.services.get_day_by_id_repository")
@patch("apps.routines.services.update_day_repository")
@patch("apps.routines.services.Day.objects.filter")
def test_update_day_service_success(
    self, mock_day_filter: MagicMock, mock_update_repo: MagicMock, mock_get_repo: MagicMock
) -> None:
    """Test: Actualizar día exitosamente."""
    # Arrange
    day = Day(week=self.week, day_number=1)
    day.id = 1
    mock_get_repo.return_value = day
    mock_day_filter.return_value.exclude.return_value.exists.return_value = False
    updated_day = Day(week=self.week, day_number=2)
    updated_day.id = day.id
    mock_update_repo.return_value = updated_day
    validated_data = {"dayNumber": 2}

    # Act
    result = update_day_service(day_id=day.id, validated_data=validated_data, user=self.user)

    # Assert
    self.assertEqual(result.day_number, 2)
    mock_get_repo.assert_called_once_with(day_id=day.id)
    mock_update_repo.assert_called_once()
```

#### Template de Test para Delete Service

```python
@patch("apps.routines.services.get_day_by_id_repository")
@patch("apps.routines.services.delete_day_repository")
def test_delete_day_service_success(
    self, mock_delete_repo: MagicMock, mock_get_repo: MagicMock
) -> None:
    """Test: Eliminar día exitosamente."""
    # Arrange
    day = Day(week=self.week, day_number=1)
    day.id = 1
    mock_get_repo.return_value = day

    # Act
    delete_day_service(day_id=day.id, user=self.user)

    # Assert
    mock_get_repo.assert_called_once_with(day_id=day.id)
    mock_delete_repo.assert_called_once()

@patch("apps.routines.services.get_day_by_id_repository")
def test_delete_day_service_not_found(self, mock_repo: MagicMock) -> None:
    """Test: Eliminar día inexistente."""
    # Arrange
    from rest_framework.exceptions import NotFound
    mock_repo.return_value = None

    # Act & Assert
    with self.assertRaises(NotFound):
        delete_day_service(day_id=999, user=self.user)

@patch("apps.routines.services.get_day_by_id_repository")
def test_delete_day_service_permission_denied(self, mock_repo: MagicMock) -> None:
    """Test: Eliminar día sin permisos."""
    # Arrange
    from rest_framework.exceptions import PermissionDenied
    other_user = User(username="otheruser", email="other@example.com")
    other_user.id = 2
    week = Week(routine=Routine(name="Test", created_by=other_user))
    day = Day(week=week, day_number=1)
    day.id = 1
    mock_repo.return_value = day

    # Act & Assert
    with self.assertRaises(PermissionDenied):
        delete_day_service(day_id=day.id, user=self.user)
```

---

## Mejora 5: Usar `reverse()` para URLs en Tests de API

### Objetivo
Eliminar URLs hardcodeadas y usar el sistema de reversión de URLs de Django para mejor mantenibilidad.

### Instrucciones de Implementación

#### Paso 5.1: Agregar nombres a las URLs (si no existen)

Verificar que todos los endpoints tengan `name` en `urls.py`:

```python
# apps/routines/api_urls.py
from django.urls import path
from apps.routines.views import RoutineListAPIView, RoutineDetailAPIView

urlpatterns = [
    path("", RoutineListAPIView.as_view(), name="routine-list"),
    path("<int:pk>/", RoutineDetailAPIView.as_view(), name="routine-detail"),
    # ... más URLs
]
```

#### Paso 5.2: Actualizar tests para usar reverse()

**Antes**:
```python
response = self.client.get("/api/routines/")
response = self.client.get(f"/api/routines/{self.routine.id}/")
```

**Después**:
```python
from django.urls import reverse

response = self.client.get(reverse("routine-list"))
response = self.client.get(reverse("routine-detail", kwargs={"pk": self.routine.id}))
```

#### Archivos a Modificar

- `apps/routines/tests.py` - todos los tests de API views
- `apps/exercises/tests.py` - todos los tests de API views
- `apps/users/tests.py` - todos los tests de API views

---

## Mejora 6: Agregar Tests de Errores en Repositorios

### Objetivo
Ampliar la cobertura de tests de repositorios para incluir casos de error y edge cases.

### Tests a Agregar

#### Para cada repositorio, agregar:

1. **Tests de validación de datos**:
   ```python
   def test_create_routine_repository_with_invalid_data(self) -> None:
       """Test: Crear rutina con datos inválidos."""
       # Arrange
       validated_data = {
           "name": "",  # Nombre vacío
           "durationWeeks": -1,  # Valor inválido
       }

       # Act & Assert
       with self.assertRaises(ValidationError):
           create_routine_repository(validated_data=validated_data, user=self.user)
   ```

2. **Tests de constraints de BD**:
   ```python
   def test_create_week_repository_duplicate_week_number(self) -> None:
       """Test: Crear semana con week_number duplicado."""
       # Arrange
       Week.objects.create(routine=self.routine, week_number=1)
       validated_data = {"weekNumber": 1}

       # Act & Assert
       with self.assertRaises(ValidationError):
           create_week_repository(routine_id=self.routine.id, validated_data=validated_data)
   ```

3. **Tests de actualización parcial**:
   ```python
   def test_update_routine_repository_partial_with_none_values(self) -> None:
       """Test: Actualizar rutina con valores None no debe eliminar datos."""
       # Arrange
       routine = Routine.objects.create(
           name="Original",
           description="Original description",
           created_by=self.user
       )
       validated_data = {"name": "Updated"}  # Solo actualizar name

       # Act
       updated = update_routine_repository(routine=routine, validated_data=validated_data)

       # Assert
       self.assertEqual(updated.name, "Updated")
       self.assertEqual(updated.description, "Original description")  # No debe cambiar
   ```

---

## Mejora 7: Agregar Tests de Integración End-to-End

### Objetivo
Crear tests que verifiquen flujos completos de la aplicación, desde la API hasta la base de datos.

### Instrucciones de Implementación

#### Ubicación
Crear nueva clase al final de cada archivo `tests.py`:

```python
# ============================================================================
# Tests de Integración End-to-End
# ============================================================================

class RoutineE2ETestCase(TestCase):
    """Tests de integración end-to-end para rutinas."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_create_complete_routine_flow(self) -> None:
        """Test: Crear rutina completa con semanas, días, bloques y ejercicios."""
        # Arrange
        exercise = ExerciseFactory()

        # Act - Crear rutina
        routine_data = {
            "name": "Full Routine",
            "description": "Complete routine",
            "durationWeeks": 4
        }
        routine_response = self.client.post(
            reverse("routine-list"),
            routine_data,
            format="json"
        )
        routine_id = routine_response.data["data"]["id"]

        # Act - Crear semana
        week_data = {"weekNumber": 1, "notes": "Week 1"}
        week_response = self.client.post(
            reverse("week-create", kwargs={"routine_id": routine_id}),
            week_data,
            format="json"
        )
        week_id = week_response.data["data"]["id"]

        # Act - Crear día
        day_data = {"dayNumber": 1, "name": "Day 1"}
        day_response = self.client.post(
            reverse("day-create", kwargs={"routine_id": routine_id, "week_id": week_id}),
            day_data,
            format="json"
        )
        day_id = day_response.data["data"]["id"]

        # Act - Crear bloque
        block_data = {"name": "Warm Up", "order": 1}
        block_response = self.client.post(
            reverse("block-create", kwargs={"routine_id": routine_id, "day_id": day_id}),
            block_data,
            format="json"
        )
        block_id = block_response.data["data"]["id"]

        # Act - Crear ejercicio en rutina
        exercise_data = {
            "exerciseId": exercise.id,
            "sets": 3,
            "repetitions": "10-12"
        }
        exercise_response = self.client.post(
            reverse("routine-exercise-create", kwargs={
                "routine_id": routine_id,
                "block_id": block_id
            }),
            exercise_data,
            format="json"
        )

        # Assert - Verificar toda la jerarquía
        self.assertEqual(routine_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(week_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(day_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(block_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(exercise_response.status_code, status.HTTP_201_CREATED)

        # Assert - Verificar en BD
        routine = Routine.objects.get(id=routine_id)
        self.assertEqual(routine.weeks.count(), 1)
        self.assertEqual(routine.weeks.first().days.count(), 1)
        self.assertEqual(routine.weeks.first().days.first().blocks.count(), 1)
        self.assertEqual(
            routine.weeks.first().days.first().blocks.first().routine_exercises.count(),
            1
        )

    def test_soft_delete_routine_preserves_related_data(self) -> None:
        """Test: Soft delete de rutina no elimina datos relacionados."""
        # Arrange
        routine = RoutineFactory(created_by=self.user)
        week = WeekFactory(routine=routine)
        day = DayFactory(week=week)
        block = BlockFactory(day=day)
        exercise = ExerciseFactory()
        routine_exercise = RoutineExerciseFactory(block=block, exercise=exercise)

        # Act - Soft delete de rutina
        response = self.client.delete(
            reverse("routine-detail", kwargs={"pk": routine.id})
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        routine.refresh_from_db()
        self.assertFalse(routine.is_active)  # Marcada como inactiva

        # Assert - Datos relacionados aún existen
        self.assertTrue(Week.objects.filter(id=week.id).exists())
        self.assertTrue(Day.objects.filter(id=day.id).exists())
        self.assertTrue(Block.objects.filter(id=block.id).exists())
        self.assertTrue(RoutineExercise.objects.filter(id=routine_exercise.id).exists())
```

---

## Mejora 8: Agregar Tests para Cascade Delete

### Objetivo
Verificar que las relaciones CASCADE en la base de datos funcionan correctamente.

### Tests a Agregar

```python
def test_delete_week_cascades_to_days_blocks_exercises(self) -> None:
    """Test: Eliminar semana elimina días, bloques y ejercicios en cascada."""
    # Arrange
    week = WeekFactory(routine=self.routine)
    day = DayFactory(week=week)
    block = BlockFactory(day=day)
    exercise = ExerciseFactory()
    routine_exercise = RoutineExerciseFactory(block=block, exercise=exercise)

    week_id = week.id
    day_id = day.id
    block_id = block.id
    routine_exercise_id = routine_exercise.id

    # Act
    delete_week_repository(week=week)

    # Assert - Todos los objetos relacionados deben estar eliminados
    self.assertFalse(Week.objects.filter(id=week_id).exists())
    self.assertFalse(Day.objects.filter(id=day_id).exists())
    self.assertFalse(Block.objects.filter(id=block_id).exists())
    self.assertFalse(RoutineExercise.objects.filter(id=routine_exercise_id).exists())
    # El ejercicio base NO debe eliminarse
    self.assertTrue(Exercise.objects.filter(id=exercise.id).exists())
```

Agregar tests similares para:
- `test_delete_day_cascades_to_blocks_exercises`
- `test_delete_block_cascades_to_routine_exercises`

---

## Mejora 9: Agregar SubTests para Múltiples Aserciones

### Objetivo
Mejorar la claridad de los errores cuando fallan tests con múltiples aserciones.

### Instrucciones de Implementación

**Antes**:
```python
def test_routine_serializer_success(self) -> None:
    serializer = RoutineSerializer(self.routine)
    data = serializer.data

    self.assertEqual(data["id"], self.routine.id)
    self.assertEqual(data["name"], "Rutina Test")
    self.assertEqual(data["description"], "Descripción")
    # Si falla, no sabes cuál específicamente falló
```

**Después**:
```python
def test_routine_serializer_success(self) -> None:
    serializer = RoutineSerializer(self.routine)
    data = serializer.data

    with self.subTest("Verificar id"):
        self.assertEqual(data["id"], self.routine.id)

    with self.subTest("Verificar name"):
        self.assertEqual(data["name"], "Rutina Test")

    with self.subTest("Verificar description"):
        self.assertEqual(data["description"], "Descripción")
```

---

## Mejora 10: Agregar Tests de Permisos para Vistas API Faltantes

### Objetivo
Completar cobertura de tests de permisos para todas las vistas API.

### Tests Faltantes Identificados

#### App: `routines`

Agregar tests para:
- `WeekUpdateAPIView` - update, delete
- `DayUpdateAPIView` - update, delete
- `BlockUpdateAPIView` - update, delete
- `RoutineExerciseUpdateAPIView` - update, delete

#### Template de Test

```python
def test_update_week_requires_ownership(self) -> None:
    """Test: Actualizar semana requiere ser propietario."""
    # Arrange
    other_user = UserFactory()
    routine = RoutineFactory(created_by=other_user)
    week = WeekFactory(routine=routine)
    self.client.force_authenticate(user=self.user)

    data = {"weekNumber": 2}

    # Act
    response = self.client.put(
        reverse("week-detail", kwargs={"routine_id": routine.id, "week_id": week.id}),
        data,
        format="json"
    )

    # Assert
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    self.assertIn("error", response.data)
```

---

## Resumen de Implementación

### Orden Sugerido de Implementación

1. **Primero**: Mejora 1 (Factory Pattern) - Base para simplificar el resto
2. **Segundo**: Mejora 2 (setUpTestData) - Mejora de rendimiento
3. **Tercero**: Mejora 3 (Corregir Mocks) - Correcciones críticas
4. **Cuarto**: Mejora 4 (Tests Faltantes) - Completar cobertura
5. **Quinto**: Mejoras 5-10 - Refinamiento y optimización

### Checklist de Validación

Después de implementar cada mejora, verificar:

- [ ] Todos los tests pasan: `docker compose run --rm web python manage.py test`
- [ ] No hay imports rotos
- [ ] Los factories funcionan correctamente
- [ ] La cobertura de tests aumentó
- [ ] Los tests son más legibles y mantenibles

### Comando para Ejecutar Tests

```bash
# Ejecutar todos los tests
docker compose run --rm web python manage.py test

# Ejecutar tests de una app específica
docker compose run --rm web python manage.py test apps.routines

# Ejecutar tests con cobertura
docker compose run --rm web coverage run --source='apps' manage.py test
docker compose run --rm web coverage report
```

---

## Anexo: Convenciones de Nombres de Tests

### Patrón General
```
test_{action}_{entity}_{condition}_{expected_result}
```

### Ejemplos
```python
test_create_routine_with_valid_data_returns_routine
test_update_week_without_permission_raises_permission_denied
test_list_exercises_with_filters_returns_filtered_queryset
test_delete_routine_soft_delete_marks_inactive
```

### Convenciones por Tipo

**Tests de Modelos**:
- `test_{model}_creation_success`
- `test_{model}_str_representation`
- `test_{model}_validation_{field}_invalid`

**Tests de Repositorios**:
- `test_create_{entity}_repository_success`
- `test_get_{entity}_by_id_repository_not_found`
- `test_list_{entities}_repository_with_filters`

**Tests de Servicios**:
- `test_{action}_{entity}_service_success`
- `test_{action}_{entity}_service_not_found`
- `test_{action}_{entity}_service_permission_denied`
- `test_{action}_{entity}_service_validation_error`

**Tests de API**:
- `test_{http_method}_{endpoint}_success`
- `test_{http_method}_{endpoint}_unauthenticated`
- `test_{http_method}_{endpoint}_permission_denied`
- `test_{http_method}_{endpoint}_invalid_data`

---

## Contacto y Soporte

Para cualquier duda sobre la implementación de estas mejoras, consultar:
- Documentación del proyecto: `docs/`
- Reglas de código: `.cursor/rules/`
- Metodología AIDD: `.ai/AIDD.metodology.md`

---

**Última actualización**: 2025-11-28
**Versión**: 1.0
**Autor**: AI Code Reviewer
