from __future__ import annotations

from typing import TYPE_CHECKING

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from apps.routines.models import Routine, Week, Day, Block, RoutineExercise
from apps.routines.services import (
    list_routines_service,
    get_routine_service,
    create_routine_service,
    update_routine_service,
    delete_routine_service,
    create_week_service,
    update_week_service,
    delete_week_service,
    create_day_service,
    update_day_service,
    delete_day_service,
    create_block_service,
    update_block_service,
    delete_block_service,
    create_routine_exercise_service,
    update_routine_exercise_service,
    delete_routine_exercise_service,
    get_routine_full_service,
)
from apps.routines.repositories import (
    list_routines_repository,
    get_routine_by_id_repository,
    create_routine_repository,
    update_routine_repository,
    delete_routine_repository,
    list_weeks_by_routine_repository,
    get_week_by_id_repository,
    create_week_repository,
    update_week_repository,
    delete_week_repository,
    list_days_by_week_repository,
    get_day_by_id_repository,
    create_day_repository,
    update_day_repository,
    delete_day_repository,
    list_blocks_by_day_repository,
    get_block_by_id_repository,
    create_block_repository,
    update_block_repository,
    delete_block_repository,
    list_routine_exercises_by_block_repository,
    get_routine_exercise_by_id_repository,
    create_routine_exercise_repository,
    update_routine_exercise_repository,
    delete_routine_exercise_repository,
    get_routine_full_repository,
)
from apps.routines.serializers import (
    RoutineSerializer,
    RoutineCreateSerializer,
    RoutineUpdateSerializer,
    RoutineFullSerializer,
    WeekSerializer,
    WeekCreateSerializer,
    DaySerializer,
    DayCreateSerializer,
    BlockSerializer,
    BlockCreateSerializer,
    RoutineExerciseSerializer,
    RoutineExerciseCreateSerializer,
)

if TYPE_CHECKING:
    from apps.users.models import User
    from apps.exercises.models import Exercise

User = get_user_model()


# ============================================================================
# Tests de Modelos
# ============================================================================


class RoutineModelTestCase(TestCase):
    """Tests para el modelo Routine."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_routine_creation_success(self) -> None:
        """Test: Crear rutina exitosamente."""
        # Arrange
        routine_data = {
            "name": "Rutina de Fuerza",
            "description": "Rutina para ganar fuerza",
            "duration_weeks": 12,
            "is_active": True,
            "created_by": self.user,
        }

        # Act
        routine = Routine.objects.create(**routine_data)

        # Assert
        self.assertEqual(routine.name, "Rutina de Fuerza")
        self.assertEqual(routine.description, "Rutina para ganar fuerza")
        self.assertEqual(routine.duration_weeks, 12)
        self.assertTrue(routine.is_active)
        self.assertEqual(routine.created_by, self.user)
        self.assertIsNotNone(routine.created_at)
        self.assertIsNotNone(routine.updated_at)

    def test_routine_str_representation(self) -> None:
        """Test: Representación string de rutina."""
        # Arrange
        routine = Routine.objects.create(
            name="Rutina Test", created_by=self.user
        )

        # Act
        str_repr = str(routine)

        # Assert
        self.assertEqual(str_repr, "Rutina Test")

    def test_routine_default_is_active(self) -> None:
        """Test: is_active por defecto es True."""
        # Arrange & Act
        routine = Routine.objects.create(name="Rutina Test", created_by=self.user)

        # Assert
        self.assertTrue(routine.is_active)


class WeekModelTestCase(TestCase):
    """Tests para el modelo Week."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(
            name="Rutina Test", created_by=self.user
        )

    def test_week_creation_success(self) -> None:
        """Test: Crear semana exitosamente."""
        # Arrange
        week_data = {
            "routine": self.routine,
            "week_number": 1,
            "notes": "Primera semana",
        }

        # Act
        week = Week.objects.create(**week_data)

        # Assert
        self.assertEqual(week.routine, self.routine)
        self.assertEqual(week.week_number, 1)
        self.assertEqual(week.notes, "Primera semana")
        self.assertIsNotNone(week.created_at)

    def test_week_str_representation(self) -> None:
        """Test: Representación string de semana."""
        # Arrange
        week = Week.objects.create(routine=self.routine, week_number=1)

        # Act
        str_repr = str(week)

        # Assert
        self.assertIn("Week 1", str_repr)
        self.assertIn("Rutina Test", str_repr)

    def test_week_unique_together_constraint(self) -> None:
        """Test: week_number debe ser único por rutina."""
        # Arrange
        Week.objects.create(routine=self.routine, week_number=1)

        # Act & Assert
        with self.assertRaises(ValidationError):
            week = Week(routine=self.routine, week_number=1)
            week.full_clean()
            week.save()

    def test_week_clean_validation_duplicate_week_number(self) -> None:
        """Test: Validación clean detecta week_number duplicado."""
        # Arrange
        Week.objects.create(routine=self.routine, week_number=1)

        # Act
        week = Week(routine=self.routine, week_number=1)

        # Assert
        with self.assertRaises(ValidationError) as context:
            week.clean()

        self.assertIn("week_number", str(context.exception))

    def test_week_ordering(self) -> None:
        """Test: Semanas ordenadas por week_number."""
        # Arrange
        Week.objects.create(routine=self.routine, week_number=3)
        Week.objects.create(routine=self.routine, week_number=1)
        Week.objects.create(routine=self.routine, week_number=2)

        # Act
        weeks = list(Week.objects.filter(routine=self.routine))

        # Assert
        self.assertEqual(weeks[0].week_number, 1)
        self.assertEqual(weeks[1].week_number, 2)
        self.assertEqual(weeks[2].week_number, 3)


class DayModelTestCase(TestCase):
    """Tests para el modelo Day."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(
            name="Rutina Test", created_by=self.user
        )
        self.week = Week.objects.create(routine=self.routine, week_number=1)

    def test_day_creation_success(self) -> None:
        """Test: Crear día exitosamente."""
        # Arrange
        day_data = {
            "week": self.week,
            "day_number": 1,
            "name": "Día 1",
            "notes": "Día de pecho",
        }

        # Act
        day = Day.objects.create(**day_data)

        # Assert
        self.assertEqual(day.week, self.week)
        self.assertEqual(day.day_number, 1)
        self.assertEqual(day.name, "Día 1")
        self.assertEqual(day.notes, "Día de pecho")

    def test_day_str_representation_with_name(self) -> None:
        """Test: Representación string de día con nombre."""
        # Arrange
        day = Day.objects.create(week=self.week, day_number=1, name="Día 1")

        # Act
        str_repr = str(day)

        # Assert
        self.assertIn("Día 1", str_repr)

    def test_day_str_representation_without_name(self) -> None:
        """Test: Representación string de día sin nombre."""
        # Arrange
        day = Day.objects.create(week=self.week, day_number=1)

        # Act
        str_repr = str(day)

        # Assert
        self.assertIn("Día 1", str_repr)

    def test_day_unique_together_constraint(self) -> None:
        """Test: day_number debe ser único por semana."""
        # Arrange
        Day.objects.create(week=self.week, day_number=1)

        # Act & Assert
        with self.assertRaises(ValidationError):
            day = Day(week=self.week, day_number=1)
            day.full_clean()
            day.save()

    def test_day_clean_validation_duplicate_day_number(self) -> None:
        """Test: Validación clean detecta day_number duplicado."""
        # Arrange
        Day.objects.create(week=self.week, day_number=1)

        # Act
        day = Day(week=self.week, day_number=1)

        # Assert
        with self.assertRaises(ValidationError) as context:
            day.clean()

        self.assertIn("day_number", str(context.exception))

    def test_day_ordering(self) -> None:
        """Test: Días ordenados por day_number."""
        # Arrange
        Day.objects.create(week=self.week, day_number=3)
        Day.objects.create(week=self.week, day_number=1)
        Day.objects.create(week=self.week, day_number=2)

        # Act
        days = list(Day.objects.filter(week=self.week))

        # Assert
        self.assertEqual(days[0].day_number, 1)
        self.assertEqual(days[1].day_number, 2)
        self.assertEqual(days[2].day_number, 3)


class BlockModelTestCase(TestCase):
    """Tests para el modelo Block."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(
            name="Rutina Test", created_by=self.user
        )
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)

    def test_block_creation_success(self) -> None:
        """Test: Crear bloque exitosamente."""
        # Arrange
        block_data = {
            "day": self.day,
            "name": "Calentamiento",
            "order": 1,
            "notes": "Bloque de calentamiento",
        }

        # Act
        block = Block.objects.create(**block_data)

        # Assert
        self.assertEqual(block.day, self.day)
        self.assertEqual(block.name, "Calentamiento")
        self.assertEqual(block.order, 1)
        self.assertEqual(block.notes, "Bloque de calentamiento")

    def test_block_str_representation(self) -> None:
        """Test: Representación string de bloque."""
        # Arrange
        block = Block.objects.create(day=self.day, name="Calentamiento")

        # Act
        str_repr = str(block)

        # Assert
        self.assertIn("Calentamiento", str_repr)

    def test_block_auto_assign_order_when_none(self) -> None:
        """Test: order se asigna automáticamente si no se proporciona."""
        # Arrange
        Block.objects.create(day=self.day, name="Bloque 1", order=1)

        # Act
        block = Block(day=self.day, name="Bloque 2")
        block.save()

        # Assert
        self.assertEqual(block.order, 2)

    def test_block_auto_assign_order_first_block(self) -> None:
        """Test: order se asigna a 1 para el primer bloque."""
        # Arrange & Act
        block = Block(day=self.day, name="Primer Bloque")
        block.save()

        # Assert
        self.assertEqual(block.order, 1)

    def test_block_ordering(self) -> None:
        """Test: Bloques ordenados por order e id."""
        # Arrange
        Block.objects.create(day=self.day, name="Bloque 3", order=3)
        Block.objects.create(day=self.day, name="Bloque 1", order=1)
        Block.objects.create(day=self.day, name="Bloque 2", order=2)

        # Act
        blocks = list(Block.objects.filter(day=self.day))

        # Assert
        self.assertEqual(blocks[0].order, 1)
        self.assertEqual(blocks[1].order, 2)
        self.assertEqual(blocks[2].order, 3)


class RoutineExerciseModelTestCase(TestCase):
    """Tests para el modelo RoutineExercise."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(
            name="Rutina Test", created_by=self.user
        )
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)
        self.block = Block.objects.create(day=self.day, name="Bloque 1")

        # Crear ejercicio de prueba
        from apps.exercises.models import Exercise

        self.exercise = Exercise.objects.create(
            name="Press de Banca",
            description="Ejercicio de pecho",
            created_by=self.user,
        )

    def test_routine_exercise_creation_success(self) -> None:
        """Test: Crear ejercicio en rutina exitosamente."""
        # Arrange
        routine_exercise_data = {
            "block": self.block,
            "exercise": self.exercise,
            "order": 1,
            "sets": 3,
            "repetitions": "8-10",
            "weight": 80.0,
            "rest_seconds": 90,
        }

        # Act
        routine_exercise = RoutineExercise.objects.create(**routine_exercise_data)

        # Assert
        self.assertEqual(routine_exercise.block, self.block)
        self.assertEqual(routine_exercise.exercise, self.exercise)
        self.assertEqual(routine_exercise.order, 1)
        self.assertEqual(routine_exercise.sets, 3)
        self.assertEqual(routine_exercise.repetitions, "8-10")
        self.assertEqual(float(routine_exercise.weight), 80.0)
        self.assertEqual(routine_exercise.rest_seconds, 90)

    def test_routine_exercise_str_representation(self) -> None:
        """Test: Representación string de ejercicio en rutina."""
        # Arrange
        routine_exercise = RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise
        )

        # Act
        str_repr = str(routine_exercise)

        # Assert
        self.assertIn("Press de Banca", str_repr)

    def test_routine_exercise_auto_assign_order_when_none(self) -> None:
        """Test: order se asigna automáticamente si no se proporciona."""
        # Arrange
        RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise, order=1
        )

        # Act
        routine_exercise = RoutineExercise(block=self.block, exercise=self.exercise)
        routine_exercise.save()

        # Assert
        self.assertEqual(routine_exercise.order, 2)

    def test_routine_exercise_auto_assign_order_first_exercise(self) -> None:
        """Test: order se asigna a 1 para el primer ejercicio."""
        # Arrange & Act
        routine_exercise = RoutineExercise(block=self.block, exercise=self.exercise)
        routine_exercise.save()

        # Assert
        self.assertEqual(routine_exercise.order, 1)

    def test_routine_exercise_ordering(self) -> None:
        """Test: Ejercicios ordenados por order e id."""
        # Arrange
        RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise, order=3
        )
        RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise, order=1
        )
        RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise, order=2
        )

        # Act
        exercises = list(RoutineExercise.objects.filter(block=self.block))

        # Assert
        self.assertEqual(exercises[0].order, 1)
        self.assertEqual(exercises[1].order, 2)
        self.assertEqual(exercises[2].order, 3)


# ============================================================================
# Tests de Repositorios
# ============================================================================


class RoutineRepositoryTestCase(TestCase):
    """Tests para repositorios de Routine."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

    def test_list_routines_repository_with_user(self) -> None:
        """Test: Listar rutinas filtradas por usuario."""
        # Arrange
        Routine.objects.create(name="Rutina 1", created_by=self.user)
        Routine.objects.create(name="Rutina 2", created_by=self.user)
        Routine.objects.create(name="Rutina 3", created_by=self.other_user)

        # Act
        routines = list_routines_repository(user=self.user)

        # Assert
        self.assertEqual(routines.count(), 2)
        self.assertTrue(all(r.created_by == self.user for r in routines))

    def test_list_routines_repository_without_user(self) -> None:
        """Test: Listar todas las rutinas sin filtro de usuario."""
        # Arrange
        Routine.objects.create(name="Rutina 1", created_by=self.user)
        Routine.objects.create(name="Rutina 2", created_by=self.other_user)

        # Act
        routines = list_routines_repository()

        # Assert
        self.assertEqual(routines.count(), 2)

    def test_list_routines_repository_with_is_active_filter(self) -> None:
        """Test: Listar rutinas filtradas por is_active."""
        # Arrange
        Routine.objects.create(name="Rutina Activa", created_by=self.user, is_active=True)
        Routine.objects.create(name="Rutina Inactiva", created_by=self.user, is_active=False)

        # Act
        active_routines = list_routines_repository(
            user=self.user, filters={"isActive": True}
        )
        inactive_routines = list_routines_repository(
            user=self.user, filters={"isActive": False}
        )

        # Assert
        self.assertEqual(active_routines.count(), 1)
        self.assertEqual(inactive_routines.count(), 1)
        self.assertTrue(active_routines.first().is_active)
        self.assertFalse(inactive_routines.first().is_active)

    def test_get_routine_by_id_repository_success(self) -> None:
        """Test: Obtener rutina por ID exitosamente."""
        # Arrange
        routine = Routine.objects.create(name="Rutina Test", created_by=self.user)

        # Act
        result = get_routine_by_id_repository(routine_id=routine.id)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, routine.id)
        self.assertEqual(result.name, "Rutina Test")

    def test_get_routine_by_id_repository_not_found(self) -> None:
        """Test: Obtener rutina por ID inexistente."""
        # Arrange & Act
        result = get_routine_by_id_repository(routine_id=999)

        # Assert
        self.assertIsNone(result)

    def test_create_routine_repository_success(self) -> None:
        """Test: Crear rutina exitosamente."""
        # Arrange
        validated_data = {
            "name": "Nueva Rutina",
            "description": "Descripción",
            "durationWeeks": 12,
            "isActive": True,
        }

        # Act
        routine = create_routine_repository(validated_data=validated_data, user=self.user)

        # Assert
        self.assertIsNotNone(routine.id)
        self.assertEqual(routine.name, "Nueva Rutina")
        self.assertEqual(routine.description, "Descripción")
        self.assertEqual(routine.duration_weeks, 12)
        self.assertTrue(routine.is_active)
        self.assertEqual(routine.created_by, self.user)

    def test_update_routine_repository_success(self) -> None:
        """Test: Actualizar rutina exitosamente."""
        # Arrange
        routine = Routine.objects.create(name="Rutina Original", created_by=self.user)
        validated_data = {
            "name": "Rutina Actualizada",
            "description": "Nueva descripción",
            "durationWeeks": 8,
            "isActive": False,
        }

        # Act
        updated_routine = update_routine_repository(
            routine=routine, validated_data=validated_data
        )

        # Assert
        self.assertEqual(updated_routine.name, "Rutina Actualizada")
        self.assertEqual(updated_routine.description, "Nueva descripción")
        self.assertEqual(updated_routine.duration_weeks, 8)
        self.assertFalse(updated_routine.is_active)

    def test_delete_routine_repository_soft_delete(self) -> None:
        """Test: Soft delete de rutina (marca is_active=False)."""
        # Arrange
        routine = Routine.objects.create(name="Rutina Test", created_by=self.user, is_active=True)

        # Act
        deleted_routine = delete_routine_repository(routine=routine)

        # Assert
        self.assertFalse(deleted_routine.is_active)
        self.assertIsNotNone(Routine.objects.get(id=routine.id))


class WeekRepositoryTestCase(TestCase):
    """Tests para repositorios de Week."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)

    def test_list_weeks_by_routine_repository_success(self) -> None:
        """Test: Listar semanas de una rutina."""
        # Arrange
        Week.objects.create(routine=self.routine, week_number=1)
        Week.objects.create(routine=self.routine, week_number=2)
        other_routine = Routine.objects.create(name="Otra Rutina", created_by=self.user)
        Week.objects.create(routine=other_routine, week_number=1)

        # Act
        weeks = list_weeks_by_routine_repository(routine_id=self.routine.id)

        # Assert
        self.assertEqual(weeks.count(), 2)
        self.assertTrue(all(w.routine == self.routine for w in weeks))

    def test_get_week_by_id_repository_success(self) -> None:
        """Test: Obtener semana por ID exitosamente."""
        # Arrange
        week = Week.objects.create(routine=self.routine, week_number=1)

        # Act
        result = get_week_by_id_repository(week_id=week.id)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, week.id)
        self.assertEqual(result.week_number, 1)

    def test_get_week_by_id_repository_not_found(self) -> None:
        """Test: Obtener semana por ID inexistente."""
        # Arrange & Act
        result = get_week_by_id_repository(week_id=999)

        # Assert
        self.assertIsNone(result)

    def test_create_week_repository_success(self) -> None:
        """Test: Crear semana exitosamente."""
        # Arrange
        validated_data = {"weekNumber": 1, "notes": "Primera semana"}

        # Act
        week = create_week_repository(routine_id=self.routine.id, validated_data=validated_data)

        # Assert
        self.assertIsNotNone(week.id)
        self.assertEqual(week.routine, self.routine)
        self.assertEqual(week.week_number, 1)
        self.assertEqual(week.notes, "Primera semana")

    def test_update_week_repository_success(self) -> None:
        """Test: Actualizar semana exitosamente."""
        # Arrange
        week = Week.objects.create(routine=self.routine, week_number=1)
        validated_data = {"weekNumber": 2, "notes": "Semana actualizada"}

        # Act
        updated_week = update_week_repository(week=week, validated_data=validated_data)

        # Assert
        self.assertEqual(updated_week.week_number, 2)
        self.assertEqual(updated_week.notes, "Semana actualizada")

    def test_delete_week_repository_cascade(self) -> None:
        """Test: Eliminar semana elimina días, bloques y ejercicios (CASCADE)."""
        # Arrange
        week = Week.objects.create(routine=self.routine, week_number=1)
        day = Day.objects.create(week=week, day_number=1)
        block = Block.objects.create(day=day, name="Bloque 1")
        from apps.exercises.models import Exercise

        exercise = Exercise.objects.create(name="Ejercicio", created_by=self.user)
        RoutineExercise.objects.create(block=block, exercise=exercise)

        # Act
        delete_week_repository(week=week)

        # Assert
        self.assertFalse(Week.objects.filter(id=week.id).exists())
        self.assertFalse(Day.objects.filter(id=day.id).exists())
        self.assertFalse(Block.objects.filter(id=block.id).exists())


class DayRepositoryTestCase(TestCase):
    """Tests para repositorios de Day."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)

    def test_list_days_by_week_repository_success(self) -> None:
        """Test: Listar días de una semana."""
        # Arrange
        Day.objects.create(week=self.week, day_number=1)
        Day.objects.create(week=self.week, day_number=2)
        other_week = Week.objects.create(routine=self.routine, week_number=2)
        Day.objects.create(week=other_week, day_number=1)

        # Act
        days = list_days_by_week_repository(week_id=self.week.id)

        # Assert
        self.assertEqual(days.count(), 2)
        self.assertTrue(all(d.week == self.week for d in days))

    def test_get_day_by_id_repository_success(self) -> None:
        """Test: Obtener día por ID exitosamente."""
        # Arrange
        day = Day.objects.create(week=self.week, day_number=1)

        # Act
        result = get_day_by_id_repository(day_id=day.id)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, day.id)
        self.assertEqual(result.day_number, 1)

    def test_get_day_by_id_repository_not_found(self) -> None:
        """Test: Obtener día por ID inexistente."""
        # Arrange & Act
        result = get_day_by_id_repository(day_id=999)

        # Assert
        self.assertIsNone(result)

    def test_create_day_repository_success(self) -> None:
        """Test: Crear día exitosamente."""
        # Arrange
        validated_data = {"dayNumber": 1, "name": "Día 1", "notes": "Día de pecho"}

        # Act
        day = create_day_repository(week_id=self.week.id, validated_data=validated_data)

        # Assert
        self.assertIsNotNone(day.id)
        self.assertEqual(day.week, self.week)
        self.assertEqual(day.day_number, 1)
        self.assertEqual(day.name, "Día 1")
        self.assertEqual(day.notes, "Día de pecho")

    def test_update_day_repository_success(self) -> None:
        """Test: Actualizar día exitosamente."""
        # Arrange
        day = Day.objects.create(week=self.week, day_number=1)
        validated_data = {"dayNumber": 2, "name": "Día 2", "notes": "Día actualizado"}

        # Act
        updated_day = update_day_repository(day=day, validated_data=validated_data)

        # Assert
        self.assertEqual(updated_day.day_number, 2)
        self.assertEqual(updated_day.name, "Día 2")
        self.assertEqual(updated_day.notes, "Día actualizado")

    def test_delete_day_repository_cascade(self) -> None:
        """Test: Eliminar día elimina bloques y ejercicios (CASCADE)."""
        # Arrange
        day = Day.objects.create(week=self.week, day_number=1)
        block = Block.objects.create(day=day, name="Bloque 1")
        from apps.exercises.models import Exercise

        exercise = Exercise.objects.create(name="Ejercicio", created_by=self.user)
        RoutineExercise.objects.create(block=block, exercise=exercise)

        # Act
        delete_day_repository(day=day)

        # Assert
        self.assertFalse(Day.objects.filter(id=day.id).exists())
        self.assertFalse(Block.objects.filter(id=block.id).exists())


class BlockRepositoryTestCase(TestCase):
    """Tests para repositorios de Block."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)

    def test_list_blocks_by_day_repository_success(self) -> None:
        """Test: Listar bloques de un día."""
        # Arrange
        Block.objects.create(day=self.day, name="Bloque 1", order=1)
        Block.objects.create(day=self.day, name="Bloque 2", order=2)
        other_day = Day.objects.create(week=self.week, day_number=2)
        Block.objects.create(day=other_day, name="Bloque 3", order=1)

        # Act
        blocks = list_blocks_by_day_repository(day_id=self.day.id)

        # Assert
        self.assertEqual(blocks.count(), 2)
        self.assertTrue(all(b.day == self.day for b in blocks))

    def test_get_block_by_id_repository_success(self) -> None:
        """Test: Obtener bloque por ID exitosamente."""
        # Arrange
        block = Block.objects.create(day=self.day, name="Bloque Test")

        # Act
        result = get_block_by_id_repository(block_id=block.id)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, block.id)
        self.assertEqual(result.name, "Bloque Test")

    def test_get_block_by_id_repository_not_found(self) -> None:
        """Test: Obtener bloque por ID inexistente."""
        # Arrange & Act
        result = get_block_by_id_repository(block_id=999)

        # Assert
        self.assertIsNone(result)

    def test_create_block_repository_success(self) -> None:
        """Test: Crear bloque exitosamente."""
        # Arrange
        validated_data = {"name": "Nuevo Bloque", "order": 1, "notes": "Notas"}

        # Act
        block = create_block_repository(day_id=self.day.id, validated_data=validated_data)

        # Assert
        self.assertIsNotNone(block.id)
        self.assertEqual(block.day, self.day)
        self.assertEqual(block.name, "Nuevo Bloque")
        self.assertEqual(block.order, 1)
        self.assertEqual(block.notes, "Notas")

    def test_update_block_repository_success(self) -> None:
        """Test: Actualizar bloque exitosamente."""
        # Arrange
        block = Block.objects.create(day=self.day, name="Bloque Original")
        validated_data = {"name": "Bloque Actualizado", "order": 2, "notes": "Notas actualizadas"}

        # Act
        updated_block = update_block_repository(block=block, validated_data=validated_data)

        # Assert
        self.assertEqual(updated_block.name, "Bloque Actualizado")
        self.assertEqual(updated_block.order, 2)
        self.assertEqual(updated_block.notes, "Notas actualizadas")

    def test_delete_block_repository_cascade(self) -> None:
        """Test: Eliminar bloque elimina ejercicios (CASCADE)."""
        # Arrange
        block = Block.objects.create(day=self.day, name="Bloque 1")
        from apps.exercises.models import Exercise

        exercise = Exercise.objects.create(name="Ejercicio", created_by=self.user)
        RoutineExercise.objects.create(block=block, exercise=exercise)

        # Act
        delete_block_repository(block=block)

        # Assert
        self.assertFalse(Block.objects.filter(id=block.id).exists())


class RoutineExerciseRepositoryTestCase(TestCase):
    """Tests para repositorios de RoutineExercise."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)
        self.block = Block.objects.create(day=self.day, name="Bloque 1")

        from apps.exercises.models import Exercise

        self.exercise = Exercise.objects.create(name="Ejercicio Test", created_by=self.user)

    def test_list_routine_exercises_by_block_repository_success(self) -> None:
        """Test: Listar ejercicios de un bloque."""
        # Arrange
        RoutineExercise.objects.create(block=self.block, exercise=self.exercise, order=1)
        RoutineExercise.objects.create(block=self.block, exercise=self.exercise, order=2)
        other_block = Block.objects.create(day=self.day, name="Bloque 2")
        RoutineExercise.objects.create(block=other_block, exercise=self.exercise, order=1)

        # Act
        exercises = list_routine_exercises_by_block_repository(block_id=self.block.id)

        # Assert
        self.assertEqual(exercises.count(), 2)
        self.assertTrue(all(e.block == self.block for e in exercises))

    def test_get_routine_exercise_by_id_repository_success(self) -> None:
        """Test: Obtener ejercicio en rutina por ID exitosamente."""
        # Arrange
        routine_exercise = RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise
        )

        # Act
        result = get_routine_exercise_by_id_repository(
            routine_exercise_id=routine_exercise.id
        )

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, routine_exercise.id)
        self.assertEqual(result.exercise, self.exercise)

    def test_get_routine_exercise_by_id_repository_not_found(self) -> None:
        """Test: Obtener ejercicio en rutina por ID inexistente."""
        # Arrange & Act
        result = get_routine_exercise_by_id_repository(routine_exercise_id=999)

        # Assert
        self.assertIsNone(result)

    def test_create_routine_exercise_repository_success(self) -> None:
        """Test: Crear ejercicio en rutina exitosamente."""
        # Arrange
        validated_data = {
            "order": 1,
            "sets": 3,
            "repetitions": "8-10",
            "weight": 80.0,
            "restSeconds": 90,
        }

        # Act
        routine_exercise = create_routine_exercise_repository(
            block_id=self.block.id,
            exercise_id=self.exercise.id,
            validated_data=validated_data,
        )

        # Assert
        self.assertIsNotNone(routine_exercise.id)
        self.assertEqual(routine_exercise.block, self.block)
        self.assertEqual(routine_exercise.exercise, self.exercise)
        self.assertEqual(routine_exercise.sets, 3)
        self.assertEqual(routine_exercise.repetitions, "8-10")
        self.assertEqual(float(routine_exercise.weight), 80.0)
        self.assertEqual(routine_exercise.rest_seconds, 90)

    def test_update_routine_exercise_repository_success(self) -> None:
        """Test: Actualizar ejercicio en rutina exitosamente."""
        # Arrange
        routine_exercise = RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise, sets=3
        )
        validated_data = {
            "sets": 4,
            "repetitions": "10-12",
            "weight": 85.0,
            "restSeconds": 120,
        }

        # Act
        updated_routine_exercise = update_routine_exercise_repository(
            routine_exercise=routine_exercise, validated_data=validated_data
        )

        # Assert
        self.assertEqual(updated_routine_exercise.sets, 4)
        self.assertEqual(updated_routine_exercise.repetitions, "10-12")
        self.assertEqual(float(updated_routine_exercise.weight), 85.0)
        self.assertEqual(updated_routine_exercise.rest_seconds, 120)

    def test_get_routine_full_repository_success(self) -> None:
        """Test: Obtener rutina completa con jerarquía."""
        # Arrange
        # Usar week_number=2 para evitar conflicto con setUp que crea week_number=1
        week = Week.objects.create(routine=self.routine, week_number=2)
        day = Day.objects.create(week=week, day_number=1)
        block = Block.objects.create(day=day, name="Bloque 1")
        RoutineExercise.objects.create(block=block, exercise=self.exercise)

        # Act
        routine = get_routine_full_repository(routine_id=self.routine.id)

        # Assert
        self.assertIsNotNone(routine)
        self.assertEqual(routine.id, self.routine.id)
        self.assertEqual(routine.weeks.count(), 2)  # Incluye la del setUp
        # Verificar que la semana creada en el test existe
        week_ids = [w.id for w in routine.weeks.all()]
        self.assertIn(week.id, week_ids)

    def test_get_routine_full_repository_not_found(self) -> None:
        """Test: Obtener rutina completa inexistente."""
        # Arrange & Act
        result = get_routine_full_repository(routine_id=999)

        # Assert
        self.assertIsNone(result)


# ============================================================================
# Tests de Servicios (con mocks)
# ============================================================================


class RoutineServiceTestCase(TestCase):
    """Tests para servicios de Routine con mocks."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    @patch("apps.routines.services.list_routines_repository")
    def test_list_routines_service_success(self, mock_repo: MagicMock) -> None:
        """Test: Listar rutinas exitosamente."""
        # Arrange
        routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        mock_repo.return_value = [routine]

        # Act
        result = list_routines_service(user=self.user)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Rutina Test")
        mock_repo.assert_called_once_with(user=self.user)

    @patch("apps.routines.services.get_routine_by_id_repository")
    def test_get_routine_service_success(self, mock_repo: MagicMock) -> None:
        """Test: Obtener rutina exitosamente."""
        # Arrange
        routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        mock_repo.return_value = routine

        # Act
        result = get_routine_service(routine_id=routine.id, user=self.user)

        # Assert
        self.assertEqual(result.id, routine.id)
        self.assertEqual(result.name, "Rutina Test")
        mock_repo.assert_called_once_with(routine_id=routine.id)

    @patch("apps.routines.services.get_routine_by_id_repository")
    def test_get_routine_service_not_found(self, mock_repo: MagicMock) -> None:
        """Test: Obtener rutina inexistente."""
        # Arrange
        from rest_framework.exceptions import NotFound

        mock_repo.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            get_routine_service(routine_id=999, user=self.user)

    @patch("apps.routines.services.get_routine_by_id_repository")
    def test_get_routine_service_permission_denied(self, mock_repo: MagicMock) -> None:
        """Test: Obtener rutina de otro usuario."""
        # Arrange
        from rest_framework.exceptions import NotFound

        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        routine = Routine.objects.create(name="Rutina Test", created_by=other_user)
        mock_repo.return_value = routine

        # Act & Assert
        with self.assertRaises(NotFound):
            get_routine_service(routine_id=routine.id, user=self.user)

    @patch("apps.routines.services.create_routine_repository")
    def test_create_routine_service_success(self, mock_repo: MagicMock) -> None:
        """Test: Crear rutina exitosamente."""
        # Arrange
        validated_data = {"name": "Nueva Rutina", "description": "Descripción"}
        routine = Routine.objects.create(name="Nueva Rutina", created_by=self.user)
        mock_repo.return_value = routine

        # Act
        result = create_routine_service(validated_data=validated_data, user=self.user)

        # Assert
        self.assertEqual(result.name, "Nueva Rutina")
        mock_repo.assert_called_once_with(validated_data=validated_data, user=self.user)

    @patch("apps.routines.services.create_routine_repository")
    def test_create_routine_service_validation_error_no_name(self, mock_repo: MagicMock) -> None:
        """Test: Crear rutina sin nombre lanza ValidationError."""
        # Arrange
        from rest_framework.exceptions import ValidationError

        validated_data = {"description": "Sin nombre"}

        # Act & Assert
        with self.assertRaises(ValidationError):
            create_routine_service(validated_data=validated_data, user=self.user)

        mock_repo.assert_not_called()

    @patch("apps.routines.services.get_routine_by_id_repository")
    @patch("apps.routines.services.update_routine_repository")
    def test_update_routine_service_success(
        self, mock_update_repo: MagicMock, mock_get_repo: MagicMock
    ) -> None:
        """Test: Actualizar rutina exitosamente."""
        # Arrange
        routine = Routine.objects.create(name="Rutina Original", created_by=self.user)
        mock_get_repo.return_value = routine
        updated_routine = Routine.objects.create(name="Rutina Actualizada", created_by=self.user)
        mock_update_repo.return_value = updated_routine
        validated_data = {"name": "Rutina Actualizada"}

        # Act
        result = update_routine_service(
            routine_id=routine.id, validated_data=validated_data, user=self.user
        )

        # Assert
        self.assertEqual(result.name, "Rutina Actualizada")
        mock_get_repo.assert_called_once_with(routine_id=routine.id)
        mock_update_repo.assert_called_once()

    @patch("apps.routines.services.get_routine_by_id_repository")
    def test_update_routine_service_not_found(self, mock_repo: MagicMock) -> None:
        """Test: Actualizar rutina inexistente."""
        # Arrange
        from rest_framework.exceptions import NotFound

        mock_repo.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            update_routine_service(
                routine_id=999, validated_data={"name": "Test"}, user=self.user
            )

    @patch("apps.routines.services.get_routine_by_id_repository")
    def test_update_routine_service_permission_denied(self, mock_repo: MagicMock) -> None:
        """Test: Actualizar rutina de otro usuario."""
        # Arrange
        from rest_framework.exceptions import PermissionDenied

        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        routine = Routine.objects.create(name="Rutina Test", created_by=other_user)
        mock_repo.return_value = routine

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            update_routine_service(
                routine_id=routine.id, validated_data={"name": "Test"}, user=self.user
            )

    @patch("apps.routines.services.get_routine_by_id_repository")
    @patch("apps.routines.services.delete_routine_repository")
    def test_delete_routine_service_success(
        self, mock_delete_repo: MagicMock, mock_get_repo: MagicMock
    ) -> None:
        """Test: Eliminar rutina exitosamente."""
        # Arrange
        routine = Routine.objects.create(name="Rutina Test", created_by=self.user, is_active=True)
        mock_get_repo.return_value = routine
        deleted_routine = Routine.objects.create(name="Rutina Test", created_by=self.user, is_active=False)
        mock_delete_repo.return_value = deleted_routine

        # Act
        result = delete_routine_service(routine_id=routine.id, user=self.user)

        # Assert
        self.assertFalse(result.is_active)
        mock_get_repo.assert_called_once_with(routine_id=routine.id)
        mock_delete_repo.assert_called_once()

    @patch("apps.routines.services.get_routine_by_id_repository")
    def test_delete_routine_service_permission_denied(self, mock_repo: MagicMock) -> None:
        """Test: Eliminar rutina de otro usuario."""
        # Arrange
        from rest_framework.exceptions import PermissionDenied

        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        routine = Routine.objects.create(name="Rutina Test", created_by=other_user)
        mock_repo.return_value = routine

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            delete_routine_service(routine_id=routine.id, user=self.user)


class WeekServiceTestCase(TestCase):
    """Tests para servicios de Week con mocks."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)

    @patch("apps.routines.services.get_routine_by_id_repository")
    @patch("apps.routines.services.create_week_repository")
    @patch("apps.routines.services.Week.objects.filter")
    def test_create_week_service_success(
        self, mock_week_filter: MagicMock, mock_create_repo: MagicMock, mock_get_routine_repo: MagicMock
    ) -> None:
        """Test: Crear semana exitosamente."""
        # Arrange
        mock_get_routine_repo.return_value = self.routine
        # Mock para que no exista semana duplicada
        mock_week_filter.return_value.exists.return_value = False
        week = Week(routine=self.routine, week_number=2)
        week.id = 1  # Simular ID sin guardar en BD
        mock_create_repo.return_value = week
        validated_data = {"weekNumber": 2, "notes": "Segunda semana"}

        # Act
        result = create_week_service(
            routine_id=self.routine.id, validated_data=validated_data, user=self.user
        )

        # Assert
        self.assertEqual(result.week_number, 2)
        mock_get_routine_repo.assert_called_once_with(routine_id=self.routine.id)
        mock_create_repo.assert_called_once()

    @patch("apps.routines.services.get_routine_by_id_repository")
    def test_create_week_service_routine_not_found(self, mock_repo: MagicMock) -> None:
        """Test: Crear semana en rutina inexistente."""
        # Arrange
        from rest_framework.exceptions import NotFound

        mock_repo.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            create_week_service(
                routine_id=999, validated_data={"weekNumber": 1}, user=self.user
            )

    @patch("apps.routines.services.get_routine_by_id_repository")
    @patch("apps.routines.services.Week.objects.filter")
    def test_create_week_service_duplicate_week_number(
        self, mock_week_filter: MagicMock, mock_repo: MagicMock
    ) -> None:
        """Test: Crear semana con weekNumber duplicado."""
        # Arrange
        from rest_framework.exceptions import ValidationError

        mock_repo.return_value = self.routine
        # Mock para simular que ya existe una semana con week_number=1
        mock_week_filter.return_value.exists.return_value = True

        # Act & Assert
        with self.assertRaises(ValidationError):
            create_week_service(
                routine_id=self.routine.id, validated_data={"weekNumber": 1}, user=self.user
            )

    @patch("apps.routines.services.get_week_by_id_repository")
    @patch("apps.routines.services.update_week_repository")
    @patch("apps.routines.services.Week.objects.filter")
    def test_update_week_service_success(
        self, mock_week_filter: MagicMock, mock_update_repo: MagicMock, mock_get_repo: MagicMock
    ) -> None:
        """Test: Actualizar semana exitosamente."""
        # Arrange
        # Mockear la semana existente en lugar de crearla en la BD
        week = Week(routine=self.routine, week_number=1)
        week.id = 1  # Simular ID sin guardar en BD
        mock_get_repo.return_value = week
        # Mock para que no exista semana duplicada al actualizar
        mock_week_filter.return_value.exclude.return_value.exists.return_value = False
        updated_week = Week(routine=self.routine, week_number=2)
        updated_week.id = week.id
        mock_update_repo.return_value = updated_week
        validated_data = {"weekNumber": 2}

        # Act
        result = update_week_service(week_id=week.id, validated_data=validated_data, user=self.user)

        # Assert
        self.assertEqual(result.week_number, 2)
        mock_get_repo.assert_called_once_with(week_id=week.id)
        mock_update_repo.assert_called_once()

    @patch("apps.routines.services.get_week_by_id_repository")
    @patch("apps.routines.services.delete_week_repository")
    def test_delete_week_service_success(
        self, mock_delete_repo: MagicMock, mock_get_repo: MagicMock
    ) -> None:
        """Test: Eliminar semana exitosamente."""
        # Arrange
        week = Week.objects.create(routine=self.routine, week_number=1)
        mock_get_repo.return_value = week

        # Act
        delete_week_service(week_id=week.id, user=self.user)

        # Assert
        mock_get_repo.assert_called_once_with(week_id=week.id)
        mock_delete_repo.assert_called_once()


class DayServiceTestCase(TestCase):
    """Tests para servicios de Day con mocks."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)

    @patch("apps.routines.services.get_week_by_id_repository")
    @patch("apps.routines.services.create_day_repository")
    @patch("apps.routines.services.Day.objects.filter")
    def test_create_day_service_success(
        self, mock_day_filter: MagicMock, mock_create_repo: MagicMock, mock_get_week_repo: MagicMock
    ) -> None:
        """Test: Crear día exitosamente."""
        # Arrange
        mock_get_week_repo.return_value = self.week
        # Mock para que no exista día duplicado
        mock_day_filter.return_value.exists.return_value = False
        day = Day(week=self.week, day_number=1)
        day.id = 1  # Simular ID sin guardar en BD
        mock_create_repo.return_value = day
        validated_data = {"dayNumber": 1, "name": "Día 1"}

        # Act
        result = create_day_service(
            week_id=self.week.id, validated_data=validated_data, user=self.user
        )

        # Assert
        self.assertEqual(result.day_number, 1)
        mock_get_week_repo.assert_called_once_with(week_id=self.week.id)
        mock_create_repo.assert_called_once()

    @patch("apps.routines.services.get_week_by_id_repository")
    def test_create_day_service_duplicate_day_number(self, mock_repo: MagicMock) -> None:
        """Test: Crear día con dayNumber duplicado."""
        # Arrange
        from rest_framework.exceptions import ValidationError

        mock_repo.return_value = self.week
        Day.objects.create(week=self.week, day_number=1)

        # Act & Assert
        with self.assertRaises(ValidationError):
            create_day_service(
                week_id=self.week.id, validated_data={"dayNumber": 1}, user=self.user
            )


class BlockServiceTestCase(TestCase):
    """Tests para servicios de Block con mocks."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)

    @patch("apps.routines.services.get_day_by_id_repository")
    @patch("apps.routines.services.create_block_repository")
    def test_create_block_service_success(
        self, mock_create_repo: MagicMock, mock_get_day_repo: MagicMock
    ) -> None:
        """Test: Crear bloque exitosamente."""
        # Arrange
        mock_get_day_repo.return_value = self.day
        block = Block.objects.create(day=self.day, name="Bloque 1")
        mock_create_repo.return_value = block
        validated_data = {"name": "Bloque 1", "order": 1}

        # Act
        result = create_block_service(
            day_id=self.day.id, validated_data=validated_data, user=self.user
        )

        # Assert
        self.assertEqual(result.name, "Bloque 1")
        mock_get_day_repo.assert_called_once_with(day_id=self.day.id)
        mock_create_repo.assert_called_once()


class RoutineExerciseServiceTestCase(TestCase):
    """Tests para servicios de RoutineExercise con mocks."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)
        self.block = Block.objects.create(day=self.day, name="Bloque 1")

        from apps.exercises.models import Exercise

        self.exercise = Exercise.objects.create(name="Ejercicio Test", created_by=self.user)

    @patch("apps.routines.services.get_exercise_by_id_repository")
    @patch("apps.routines.services.get_block_by_id_repository")
    @patch("apps.routines.services.create_routine_exercise_repository")
    def test_create_routine_exercise_service_success(
        self,
        mock_create_repo: MagicMock,
        mock_get_block_repo: MagicMock,
        mock_get_exercise_repo: MagicMock,
    ) -> None:
        """Test: Crear ejercicio en rutina exitosamente."""
        # Arrange
        mock_get_block_repo.return_value = self.block
        mock_get_exercise_repo.return_value = self.exercise
        routine_exercise = RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise
        )
        mock_create_repo.return_value = routine_exercise
        validated_data = {"sets": 3, "repetitions": "8-10"}

        # Act
        result = create_routine_exercise_service(
            block_id=self.block.id,
            exercise_id=self.exercise.id,
            validated_data=validated_data,
            user=self.user,
        )

        # Assert
        self.assertEqual(result.block, self.block)
        self.assertEqual(result.exercise, self.exercise)
        mock_get_block_repo.assert_called_once_with(block_id=self.block.id)
        mock_get_exercise_repo.assert_called_once_with(exercise_id=self.exercise.id)
        mock_create_repo.assert_called_once()

    @patch("apps.routines.services.get_block_by_id_repository")
    def test_create_routine_exercise_service_block_not_found(self, mock_repo: MagicMock) -> None:
        """Test: Crear ejercicio en bloque inexistente."""
        # Arrange
        from rest_framework.exceptions import NotFound

        mock_repo.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            create_routine_exercise_service(
                block_id=999, exercise_id=self.exercise.id, validated_data={}, user=self.user
            )

    @patch("apps.routines.services.get_exercise_by_id_repository")
    @patch("apps.routines.services.get_block_by_id_repository")
    def test_create_routine_exercise_service_exercise_not_found(
        self, mock_get_block_repo: MagicMock, mock_get_exercise_repo: MagicMock
    ) -> None:
        """Test: Crear ejercicio con ejercicio inexistente."""
        # Arrange
        from rest_framework.exceptions import NotFound

        mock_get_block_repo.return_value = self.block
        mock_get_exercise_repo.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            create_routine_exercise_service(
                block_id=self.block.id, exercise_id=999, validated_data={}, user=self.user
            )

    @patch("apps.routines.services.get_routine_full_repository")
    def test_get_routine_full_service_success(self, mock_repo: MagicMock) -> None:
        """Test: Obtener rutina completa exitosamente."""
        # Arrange
        mock_repo.return_value = self.routine

        # Act
        result = get_routine_full_service(routine_id=self.routine.id, user=self.user)

        # Assert
        self.assertEqual(result.id, self.routine.id)
        mock_repo.assert_called_once_with(routine_id=self.routine.id)

    @patch("apps.routines.services.get_routine_full_repository")
    def test_get_routine_full_service_not_found(self, mock_repo: MagicMock) -> None:
        """Test: Obtener rutina completa inexistente."""
        # Arrange
        from rest_framework.exceptions import NotFound

        mock_repo.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            get_routine_full_service(routine_id=999, user=self.user)


# ============================================================================
# Tests de Serializadores
# ============================================================================


class RoutineSerializerTestCase(TestCase):
    """Tests para serializadores de Routine."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(
            name="Rutina Test",
            description="Descripción",
            duration_weeks=12,
            duration_months=3,
            is_active=True,
            created_by=self.user,
        )

    def test_routine_serializer_success(self) -> None:
        """Test: Serializar rutina exitosamente."""
        # Arrange
        serializer = RoutineSerializer(self.routine)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.routine.id)
        self.assertEqual(data["name"], "Rutina Test")
        self.assertEqual(data["description"], "Descripción")
        self.assertEqual(data["durationWeeks"], 12)
        self.assertEqual(data["durationMonths"], 3)
        self.assertTrue(data["isActive"])
        self.assertEqual(data["createdBy"], "testuser")
        self.assertIn("createdAt", data)
        self.assertIn("updatedAt", data)

    def test_routine_create_serializer_valid_data(self) -> None:
        """Test: Validar datos válidos para crear rutina."""
        # Arrange
        data = {
            "name": "Nueva Rutina",
            "description": "Descripción",
            "durationWeeks": 12,
            "durationMonths": 3,
            "isActive": True,
        }

        # Act
        serializer = RoutineCreateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Nueva Rutina")

    def test_routine_create_serializer_invalid_name_empty(self) -> None:
        """Test: Validar nombre vacío."""
        # Arrange
        data = {"name": "   ", "description": "Descripción"}

        # Act
        serializer = RoutineCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_routine_create_serializer_missing_name(self) -> None:
        """Test: Validar nombre requerido."""
        # Arrange
        data = {"description": "Descripción"}

        # Act
        serializer = RoutineCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_routine_update_serializer_partial_update(self) -> None:
        """Test: Actualización parcial de rutina."""
        # Arrange
        data = {"name": "Rutina Actualizada"}

        # Act
        serializer = RoutineUpdateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Rutina Actualizada")


class WeekSerializerTestCase(TestCase):
    """Tests para serializadores de Week."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1, notes="Notas")

    def test_week_serializer_success(self) -> None:
        """Test: Serializar semana exitosamente."""
        # Arrange
        serializer = WeekSerializer(self.week)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.week.id)
        self.assertEqual(data["routineId"], self.routine.id)
        self.assertEqual(data["weekNumber"], 1)
        self.assertEqual(data["notes"], "Notas")
        self.assertIn("createdAt", data)
        self.assertIn("updatedAt", data)

    def test_week_create_serializer_valid_data(self) -> None:
        """Test: Validar datos válidos para crear semana."""
        # Arrange
        data = {"weekNumber": 1, "notes": "Primera semana"}

        # Act
        serializer = WeekCreateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["weekNumber"], 1)


class DaySerializerTestCase(TestCase):
    """Tests para serializadores de Day."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1, name="Día 1", notes="Notas")

    def test_day_serializer_success(self) -> None:
        """Test: Serializar día exitosamente."""
        # Arrange
        serializer = DaySerializer(self.day)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.day.id)
        self.assertEqual(data["weekId"], self.week.id)
        self.assertEqual(data["dayNumber"], 1)
        self.assertEqual(data["name"], "Día 1")
        self.assertEqual(data["notes"], "Notas")
        self.assertIn("createdAt", data)
        self.assertIn("updatedAt", data)

    def test_day_create_serializer_valid_data(self) -> None:
        """Test: Validar datos válidos para crear día."""
        # Arrange
        data = {"dayNumber": 1, "name": "Día 1", "notes": "Notas"}

        # Act
        serializer = DayCreateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["dayNumber"], 1)


class BlockSerializerTestCase(TestCase):
    """Tests para serializadores de Block."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)
        self.block = Block.objects.create(day=self.day, name="Bloque 1", order=1, notes="Notas")

    def test_block_serializer_success(self) -> None:
        """Test: Serializar bloque exitosamente."""
        # Arrange
        serializer = BlockSerializer(self.block)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.block.id)
        self.assertEqual(data["dayId"], self.day.id)
        self.assertEqual(data["name"], "Bloque 1")
        self.assertEqual(data["order"], 1)
        self.assertEqual(data["notes"], "Notas")
        self.assertIn("createdAt", data)
        self.assertIn("updatedAt", data)

    def test_block_create_serializer_valid_data(self) -> None:
        """Test: Validar datos válidos para crear bloque."""
        # Arrange
        data = {"name": "Nuevo Bloque", "order": 1, "notes": "Notas"}

        # Act
        serializer = BlockCreateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Nuevo Bloque")

    def test_block_create_serializer_invalid_name_empty(self) -> None:
        """Test: Validar nombre vacío."""
        # Arrange
        data = {"name": "   "}

        # Act
        serializer = BlockCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)


class RoutineExerciseSerializerTestCase(TestCase):
    """Tests para serializadores de RoutineExercise."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)
        self.block = Block.objects.create(day=self.day, name="Bloque 1")

        from apps.exercises.models import Exercise

        self.exercise = Exercise.objects.create(name="Ejercicio Test", created_by=self.user)
        self.routine_exercise = RoutineExercise.objects.create(
            block=self.block,
            exercise=self.exercise,
            order=1,
            sets=3,
            repetitions="8-10",
            weight=80.0,
            rest_seconds=90,
        )

    def test_routine_exercise_serializer_success(self) -> None:
        """Test: Serializar ejercicio en rutina exitosamente."""
        # Arrange
        serializer = RoutineExerciseSerializer(self.routine_exercise)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.routine_exercise.id)
        self.assertEqual(data["blockId"], self.block.id)
        self.assertEqual(data["exerciseId"], self.exercise.id)
        self.assertEqual(data["exerciseName"], "Ejercicio Test")
        self.assertEqual(data["order"], 1)
        self.assertEqual(data["sets"], 3)
        self.assertEqual(data["repetitions"], "8-10")
        self.assertEqual(float(data["weight"]), 80.0)
        self.assertEqual(data["restSeconds"], 90)
        self.assertIn("createdAt", data)
        self.assertIn("updatedAt", data)

    def test_routine_exercise_create_serializer_valid_data(self) -> None:
        """Test: Validar datos válidos para crear ejercicio en rutina."""
        # Arrange
        data = {
            "exerciseId": self.exercise.id,
            "order": 1,
            "sets": 3,
            "repetitions": "8-10",
            "weight": "80.00",
            "restSeconds": 90,
        }

        # Act
        serializer = RoutineExerciseCreateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["exerciseId"], self.exercise.id)


class RoutineFullSerializerTestCase(TestCase):
    """Tests para RoutineFullSerializer."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)
        self.block = Block.objects.create(day=self.day, name="Bloque 1")

        from apps.exercises.models import Exercise

        self.exercise = Exercise.objects.create(name="Ejercicio Test", created_by=self.user)
        RoutineExercise.objects.create(
            block=self.block, exercise=self.exercise, sets=3, repetitions="8-10"
        )

    def test_routine_full_serializer_success(self) -> None:
        """Test: Serializar rutina completa con jerarquía."""
        # Arrange
        serializer = RoutineFullSerializer(self.routine)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.routine.id)
        self.assertEqual(data["name"], "Rutina Test")
        self.assertEqual(data["createdBy"], "testuser")
        self.assertIn("weeks", data)
        self.assertEqual(len(data["weeks"]), 1)
        self.assertEqual(len(data["weeks"][0]["days"]), 1)
        self.assertEqual(len(data["weeks"][0]["days"][0]["blocks"]), 1)
        self.assertEqual(
            len(data["weeks"][0]["days"][0]["blocks"][0]["exercises"]), 1
        )


# ============================================================================
# Tests de Vistas API
# ============================================================================


class RoutineListAPIViewTestCase(TestCase):
    """Tests para RoutineListAPIView."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_routines_get_success(self) -> None:
        """Test: GET lista rutinas exitosamente."""
        # Arrange
        Routine.objects.create(name="Rutina 1", created_by=self.user)
        Routine.objects.create(name="Rutina 2", created_by=self.user)

        # Act
        response = self.client.get("/api/routines/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertIn("request", response.data)

    def test_list_routines_get_empty(self) -> None:
        """Test: GET lista vacía cuando no hay rutinas."""
        # Act
        response = self.client.get("/api/routines/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 0)

    def test_create_routine_post_success(self) -> None:
        """Test: POST crear rutina exitosamente."""
        # Arrange
        data = {
            "name": "Nueva Rutina",
            "description": "Descripción",
            "durationWeeks": 12,
            "isActive": True,
        }

        # Act
        response = self.client.post("/api/routines/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["name"], "Nueva Rutina")
        self.assertIn("message", response.data)
        self.assertIn("request", response.data)

    def test_create_routine_post_invalid_data(self) -> None:
        """Test: POST crear rutina con datos inválidos."""
        # Arrange
        data = {"description": "Sin nombre"}

        # Act
        response = self.client.post("/api/routines/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("message", response.data)

    def test_list_routines_requires_authentication(self) -> None:
        """Test: GET requiere autenticación."""
        # Arrange
        self.client.force_authenticate(user=None)

        # Act
        response = self.client.get("/api/routines/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RoutineDetailAPIViewTestCase(TestCase):
    """Tests para RoutineDetailAPIView."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)

    def test_get_routine_detail_success(self) -> None:
        """Test: GET detalle de rutina exitosamente."""
        # Act
        response = self.client.get(f"/api/routines/{self.routine.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["id"], self.routine.id)
        self.assertEqual(response.data["data"]["name"], "Rutina Test")

    def test_get_routine_detail_not_found(self) -> None:
        """Test: GET rutina inexistente."""
        # Act
        response = self.client.get("/api/routines/999/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertIn("message", response.data)

    def test_get_routine_detail_full_hierarchy(self) -> None:
        """Test: GET rutina con jerarquía completa."""
        # Arrange
        week = Week.objects.create(routine=self.routine, week_number=1)
        day = Day.objects.create(week=week, day_number=1)
        Block.objects.create(day=day, name="Bloque 1")

        # Act
        response = self.client.get(f"/api/routines/{self.routine.id}/?full=true")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("weeks", response.data["data"])

    def test_update_routine_put_success(self) -> None:
        """Test: PUT actualizar rutina exitosamente."""
        # Arrange
        data = {"name": "Rutina Actualizada", "description": "Nueva descripción"}

        # Act
        response = self.client.put(f"/api/routines/{self.routine.id}/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["name"], "Rutina Actualizada")
        self.assertIn("message", response.data)

    def test_update_routine_put_permission_denied(self) -> None:
        """Test: PUT actualizar rutina de otro usuario."""
        # Arrange
        other_routine = Routine.objects.create(name="Otra Rutina", created_by=self.other_user)
        data = {"name": "Rutina Actualizada"}

        # Act
        response = self.client.put(f"/api/routines/{other_routine.id}/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)

    def test_delete_routine_delete_success(self) -> None:
        """Test: DELETE eliminar rutina exitosamente."""
        # Act
        response = self.client.delete(f"/api/routines/{self.routine.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("message", response.data)
        routine = Routine.objects.get(id=self.routine.id)
        self.assertFalse(routine.is_active)

    def test_delete_routine_delete_permission_denied(self) -> None:
        """Test: DELETE eliminar rutina de otro usuario."""
        # Arrange
        other_routine = Routine.objects.create(name="Otra Rutina", created_by=self.other_user)

        # Act
        response = self.client.delete(f"/api/routines/{other_routine.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)


class WeekCreateAPIViewTestCase(TestCase):
    """Tests para WeekCreateAPIView."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)

    def test_create_week_post_success(self) -> None:
        """Test: POST crear semana exitosamente."""
        # Arrange
        data = {"weekNumber": 1, "notes": "Primera semana"}

        # Act
        response = self.client.post(f"/api/routines/{self.routine.id}/weeks/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["weekNumber"], 1)
        self.assertIn("message", response.data)

    def test_create_week_post_duplicate_week_number(self) -> None:
        """Test: POST crear semana con weekNumber duplicado."""
        # Arrange
        Week.objects.create(routine=self.routine, week_number=1)
        data = {"weekNumber": 1}

        # Act
        response = self.client.post(f"/api/routines/{self.routine.id}/weeks/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class DayCreateAPIViewTestCase(TestCase):
    """Tests para DayCreateAPIView."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)

    def test_create_day_post_success(self) -> None:
        """Test: POST crear día exitosamente."""
        # Arrange
        data = {"dayNumber": 1, "name": "Día 1", "notes": "Notas"}

        # Act
        response = self.client.post(
            f"/api/routines/{self.routine.id}/weeks/{self.week.id}/days/", data, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["dayNumber"], 1)
        self.assertIn("message", response.data)


class BlockCreateAPIViewTestCase(TestCase):
    """Tests para BlockCreateAPIView."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)

    def test_create_block_post_success(self) -> None:
        """Test: POST crear bloque exitosamente."""
        # Arrange
        data = {"name": "Bloque 1", "order": 1, "notes": "Notas"}

        # Act
        response = self.client.post(
            f"/api/routines/{self.routine.id}/days/{self.day.id}/blocks/", data, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["name"], "Bloque 1")
        self.assertIn("message", response.data)

    def test_create_block_post_invalid_name(self) -> None:
        """Test: POST crear bloque con nombre vacío."""
        # Arrange
        data = {"name": "   "}

        # Act
        response = self.client.post(
            f"/api/routines/{self.routine.id}/days/{self.day.id}/blocks/", data, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class RoutineExerciseCreateAPIViewTestCase(TestCase):
    """Tests para RoutineExerciseCreateAPIView."""

    def setUp(self) -> None:
        """Arrange: Configura datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.routine = Routine.objects.create(name="Rutina Test", created_by=self.user)
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)
        self.block = Block.objects.create(day=self.day, name="Bloque 1")

        from apps.exercises.models import Exercise

        self.exercise = Exercise.objects.create(name="Ejercicio Test", created_by=self.user)

    def test_create_routine_exercise_post_success(self) -> None:
        """Test: POST crear ejercicio en rutina exitosamente."""
        # Arrange
        data = {
            "exerciseId": self.exercise.id,
            "sets": 3,
            "repetitions": "8-10",
            "weight": "80.00",
            "restSeconds": 90,
        }

        # Act
        response = self.client.post(
            f"/api/routines/{self.routine.id}/blocks/{self.block.id}/exercises/",
            data,
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["exerciseId"], self.exercise.id)
        self.assertIn("message", response.data)

    def test_create_routine_exercise_post_exercise_not_found(self) -> None:
        """Test: POST crear ejercicio con ejercicio inexistente."""
        # Arrange
        data = {"exerciseId": 999, "sets": 3}

        # Act
        response = self.client.post(
            f"/api/routines/{self.routine.id}/blocks/{self.block.id}/exercises/",
            data,
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
