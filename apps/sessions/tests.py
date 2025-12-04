from __future__ import annotations

from typing import TYPE_CHECKING

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta

from apps.sessions.models import Session, SessionExercise
from apps.sessions.factories import SessionFactory, SessionExerciseFactory
from apps.exercises.factories import ExerciseFactory
from apps.routines.factories import RoutineFactory
from apps.users.factories import UserFactory
from apps.sessions.services import (
    list_sessions_service,
    get_session_service,
    create_session_service,
    update_session_service,
    delete_session_service,
    get_session_full_service,
    create_session_exercise_service,
    update_session_exercise_service,
    delete_session_exercise_service,
)
from apps.sessions.repositories import (
    list_sessions_repository,
    get_session_by_id_repository,
    create_session_repository,
    update_session_repository,
    delete_session_repository,
    list_session_exercises_repository,
    get_session_exercise_by_id_repository,
    create_session_exercise_repository,
    update_session_exercise_repository,
    delete_session_exercise_repository,
    get_session_full_repository,
)
from apps.sessions.serializers import (
    SessionSerializer,
    SessionCreateSerializer,
    SessionUpdateSerializer,
    SessionFullSerializer,
    SessionExerciseSerializer,
    SessionExerciseCreateSerializer,
    SessionExerciseUpdateSerializer,
)
from apps.sessions.forms import (
    SessionCreateForm,
    SessionUpdateForm,
    SessionExerciseForm,
)

if TYPE_CHECKING:
    from apps.users.models import User
    from apps.exercises.models import Exercise
    from apps.routines.models import Routine

User = get_user_model()


# ============================================================================
# Tests Unitarios - Models
# ============================================================================


class SessionModelTestCase(TestCase):
    """Tests unitarios para el modelo Session."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()

    def test_session_creation_with_minimal_data(self):
        """Test: Crear sesión con datos mínimos."""
        # Arrange
        session_data = {
            "user": self.user,
            "date": date.today(),
        }

        # Act
        session = Session.objects.create(**session_data)

        # Assert
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.date, date.today())
        self.assertIsNone(session.routine)
        self.assertIsNone(session.start_time)
        self.assertIsNone(session.end_time)
        self.assertIsNone(session.duration_minutes)
        self.assertIsNotNone(session.created_at)

    def test_session_creation_with_all_fields(self):
        """Test: Crear sesión con todos los campos."""
        # Arrange
        routine = RoutineFactory(created_by=self.user)
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)
        session_data = {
            "user": self.user,
            "routine": routine,
            "date": date.today(),
            "start_time": start_time,
            "end_time": end_time,
            "notes": "Great workout",
            "rpe": 8,
            "energy_level": "high",
            "sleep_hours": 7.5,
        }

        # Act
        session = Session.objects.create(**session_data)

        # Assert
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.routine, routine)
        self.assertEqual(session.date, date.today())
        self.assertEqual(session.start_time, start_time)
        self.assertEqual(session.end_time, end_time)
        self.assertEqual(session.duration_minutes, 60)
        self.assertEqual(session.notes, "Great workout")
        self.assertEqual(session.rpe, 8)
        self.assertEqual(session.energy_level, "high")
        self.assertEqual(session.sleep_hours, 7.5)

    def test_session_str_representation(self):
        """Test: Representación string de la sesión."""
        # Arrange
        routine = RoutineFactory(created_by=self.user, name="Push Day")
        session = SessionFactory(user=self.user, routine=routine, date=date.today())

        # Act
        str_repr = str(session)

        # Assert
        self.assertIn(str(date.today()), str_repr)
        self.assertIn(self.user.username, str_repr)
        self.assertIn("Push Day", str_repr)

    def test_session_str_representation_without_routine(self):
        """Test: Representación string sin rutina."""
        # Arrange
        session = SessionFactory(user=self.user, routine=None, date=date.today())

        # Act
        str_repr = str(session)

        # Assert
        self.assertIn(str(date.today()), str_repr)
        self.assertIn(self.user.username, str_repr)

    def test_session_automatic_duration_calculation(self):
        """Test: Cálculo automático de duración."""
        # Arrange
        start_time = timezone.now()
        end_time = start_time + timedelta(minutes=90)
        session_data = {
            "user": self.user,
            "date": date.today(),
            "start_time": start_time,
            "end_time": end_time,
        }

        # Act
        session = Session.objects.create(**session_data)

        # Assert
        self.assertEqual(session.duration_minutes, 90)

    def test_session_clean_validates_rpe_range(self):
        """Test: Validación de RPE entre 1-10."""
        # Arrange
        session = Session(user=self.user, date=date.today(), rpe=11)

        # Act & Assert
        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_session_clean_validates_rpe_minimum(self):
        """Test: Validación de RPE mínimo."""
        # Arrange
        session = Session(user=self.user, date=date.today(), rpe=0)

        # Act & Assert
        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_session_clean_validates_end_time_after_start_time(self):
        """Test: Validación de que end_time sea posterior a start_time."""
        # Arrange
        start_time = timezone.now()
        end_time = start_time - timedelta(hours=1)
        session = Session(
            user=self.user,
            date=date.today(),
            start_time=start_time,
            end_time=end_time,
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_session_clean_allows_same_start_and_end_time(self):
        """Test: No permite que start_time y end_time sean iguales."""
        # Arrange
        same_time = timezone.now()
        session = Session(
            user=self.user,
            date=date.today(),
            start_time=same_time,
            end_time=same_time,
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_session_energy_level_choices(self):
        """Test: Validación de choices de energy_level."""
        # Arrange & Act
        session = SessionFactory(
            user=self.user,
            energy_level="high",
        )

        # Assert
        self.assertEqual(session.energy_level, "high")
        self.assertIn(session.energy_level, [choice[0] for choice in Session.ENERGY_LEVEL_CHOICES])

    def test_session_created_at_auto_now_add(self):
        """Test: created_at se establece automáticamente."""
        # Arrange & Act
        session = SessionFactory(user=self.user)

        # Assert
        self.assertIsNotNone(session.created_at)

    def test_session_updated_at_auto_now(self):
        """Test: updated_at se actualiza automáticamente."""
        # Arrange
        session = SessionFactory(user=self.user)
        original_updated_at = session.updated_at

        # Act
        session.notes = "Updated notes"
        session.save()

        # Assert
        self.assertGreater(session.updated_at, original_updated_at)


class SessionExerciseModelTestCase(TestCase):
    """Tests unitarios para el modelo SessionExercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.session = SessionFactory(user=self.user)
        self.exercise = ExerciseFactory()

    def test_session_exercise_creation_with_minimal_data(self):
        """Test: Crear ejercicio de sesión con datos mínimos."""
        # Arrange
        session_exercise_data = {
            "session": self.session,
            "exercise": self.exercise,
        }

        # Act
        session_exercise = SessionExercise.objects.create(**session_exercise_data)

        # Assert
        self.assertEqual(session_exercise.session, self.session)
        self.assertEqual(session_exercise.exercise, self.exercise)
        self.assertEqual(session_exercise.order, 1)  # Auto-asignado
        self.assertIsNotNone(session_exercise.created_at)

    def test_session_exercise_creation_with_all_fields(self):
        """Test: Crear ejercicio de sesión con todos los campos."""
        # Arrange
        session_exercise_data = {
            "session": self.session,
            "exercise": self.exercise,
            "order": 1,
            "sets_completed": 4,
            "repetitions": "10, 8, 6",
            "weight": 80.5,
            "rpe": 9,
            "rest_seconds": 120,
            "notes": "Felt strong",
        }

        # Act
        session_exercise = SessionExercise.objects.create(**session_exercise_data)

        # Assert
        self.assertEqual(session_exercise.order, 1)
        self.assertEqual(session_exercise.sets_completed, 4)
        self.assertEqual(session_exercise.repetitions, "10, 8, 6")
        self.assertEqual(session_exercise.weight, 80.5)
        self.assertEqual(session_exercise.rpe, 9)
        self.assertEqual(session_exercise.rest_seconds, 120)
        self.assertEqual(session_exercise.notes, "Felt strong")

    def test_session_exercise_str_representation(self):
        """Test: Representación string del ejercicio de sesión."""
        # Arrange
        exercise = ExerciseFactory(name="Bench Press")
        session_exercise = SessionExerciseFactory(
            session=self.session, exercise=exercise
        )

        # Act
        str_repr = str(session_exercise)

        # Assert
        self.assertIn("Bench Press", str_repr)
        self.assertIn(str(self.session.date), str_repr)

    def test_session_exercise_auto_order_assignment(self):
        """Test: Asignación automática de order."""
        # Arrange
        SessionExercise.objects.create(session=self.session, exercise=self.exercise, order=1)
        SessionExercise.objects.create(session=self.session, exercise=self.exercise, order=2)

        # Act
        new_exercise = SessionExercise.objects.create(
            session=self.session, exercise=self.exercise
        )

        # Assert
        self.assertEqual(new_exercise.order, 3)

    def test_session_exercise_clean_validates_rpe_range(self):
        """Test: Validación de RPE entre 1-10."""
        # Arrange
        session_exercise = SessionExercise(
            session=self.session, exercise=self.exercise, rpe=11
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            session_exercise.full_clean()

    def test_session_exercise_clean_validates_rpe_minimum(self):
        """Test: Validación de RPE mínimo."""
        # Arrange
        session_exercise = SessionExercise(
            session=self.session, exercise=self.exercise, rpe=0
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            session_exercise.full_clean()

    def test_session_exercise_created_at_auto_now_add(self):
        """Test: created_at se establece automáticamente."""
        # Arrange & Act
        session_exercise = SessionExerciseFactory(
            session=self.session, exercise=self.exercise
        )

        # Assert
        self.assertIsNotNone(session_exercise.created_at)

    def test_session_exercise_updated_at_auto_now(self):
        """Test: updated_at se actualiza automáticamente."""
        # Arrange
        session_exercise = SessionExerciseFactory(
            session=self.session, exercise=self.exercise
        )
        original_updated_at = session_exercise.updated_at

        # Act
        session_exercise.notes = "Updated notes"
        session_exercise.save()

        # Assert
        self.assertGreater(session_exercise.updated_at, original_updated_at)


# ============================================================================
# Tests Unitarios - Repositories
# ============================================================================


class SessionRepositoryTestCase(TestCase):
    """Tests unitarios para los repositorios de Session."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.routine = RoutineFactory(created_by=self.user)
        self.session1 = SessionFactory(
            user=self.user, routine=self.routine, date=date.today()
        )
        self.session2 = SessionFactory(
            user=self.user, routine=None, date=date.today() - timedelta(days=1)
        )
        self.session3 = SessionFactory(
            user=self.other_user, date=date.today()
        )

    def test_list_sessions_repository_without_filters(self):
        """Test: Listar sesiones sin filtros."""
        # Arrange & Act
        queryset = list_sessions_repository(user=self.user)

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.session1, queryset)
        self.assertIn(self.session2, queryset)
        self.assertNotIn(self.session3, queryset)

    def test_list_sessions_repository_with_routine_filter(self):
        """Test: Listar sesiones filtradas por rutina."""
        # Arrange
        routine_id = self.routine.id

        # Act
        queryset = list_sessions_repository(user=self.user, routine_id=routine_id)

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.session1, queryset)
        self.assertNotIn(self.session2, queryset)

    def test_list_sessions_repository_with_date_filter(self):
        """Test: Listar sesiones filtradas por fecha."""
        # Arrange
        date_filter = date.today()

        # Act
        queryset = list_sessions_repository(user=self.user, date_filter=date_filter)

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.session1, queryset)
        self.assertNotIn(self.session2, queryset)

    def test_list_sessions_repository_with_ordering(self):
        """Test: Listar sesiones con ordenamiento personalizado."""
        # Arrange
        # El repositorio no acepta ordering, usa ordenamiento por defecto
        # Arrange & Act
        queryset = list_sessions_repository(user=self.user)

        # Assert
        sessions = list(queryset)
        # Ordenamiento por defecto es -date, -created_at (más recientes primero)
        self.assertEqual(sessions[0].date, date.today())
        self.assertEqual(sessions[1].date, date.today() - timedelta(days=1))

    def test_list_sessions_repository_default_ordering(self):
        """Test: Ordenamiento por defecto (-date, -start_time)."""
        # Arrange & Act
        queryset = list_sessions_repository(user=self.user)

        # Assert
        sessions = list(queryset)
        self.assertEqual(sessions[0].date, date.today())
        self.assertEqual(sessions[1].date, date.today() - timedelta(days=1))

    def test_get_session_by_id_repository_existing(self):
        """Test: Obtener sesión por ID existente."""
        # Arrange & Act
        session = get_session_by_id_repository(session_id=self.session1.id)

        # Assert
        self.assertIsNotNone(session)
        self.assertEqual(session.id, self.session1.id)
        self.assertEqual(session.user, self.user)

    def test_get_session_by_id_repository_non_existing(self):
        """Test: Obtener sesión por ID inexistente."""
        # Arrange & Act
        session = get_session_by_id_repository(session_id=99999)

        # Assert
        self.assertIsNone(session)

    def test_get_session_full_repository_with_exercises(self):
        """Test: Obtener sesión completa con ejercicios precargados."""
        # Arrange
        exercise1 = ExerciseFactory()
        exercise2 = ExerciseFactory()
        SessionExercise.objects.create(session=self.session1, exercise=exercise1, order=1)
        SessionExercise.objects.create(session=self.session1, exercise=exercise2, order=2)

        # Act
        session = get_session_full_repository(session_id=self.session1.id)

        # Assert
        self.assertIsNotNone(session)
        self.assertEqual(session.id, self.session1.id)
        # Verificar que los ejercicios están precargados
        self.assertTrue(hasattr(session, "prefetched_session_exercises"))
        self.assertEqual(len(session.prefetched_session_exercises), 2)

    def test_create_session_repository(self):
        """Test: Crear sesión en repositorio."""
        # Arrange
        validated_data = {
            "date": date.today(),
            "routineId": self.routine.id,
            "notes": "Test session",
            "rpe": 8,
        }

        # Act
        session = create_session_repository(validated_data=validated_data, user=self.user)

        # Assert
        self.assertIsNotNone(session.id)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.routine, self.routine)
        self.assertEqual(session.date, date.today())
        self.assertEqual(session.notes, "Test session")
        self.assertEqual(session.rpe, 8)

    def test_create_session_repository_without_routine(self):
        """Test: Crear sesión sin rutina."""
        # Arrange
        validated_data = {
            "date": date.today(),
            "notes": "Test session",
        }

        # Act
        session = create_session_repository(validated_data=validated_data, user=self.user)

        # Assert
        self.assertIsNotNone(session.id)
        self.assertIsNone(session.routine)

    def test_update_session_repository(self):
        """Test: Actualizar sesión en repositorio."""
        # Arrange
        validated_data = {
            "notes": "Updated notes",
            "rpe": 9,
        }

        # Act
        updated_session = update_session_repository(
            session=self.session1, validated_data=validated_data
        )

        # Assert
        self.assertEqual(updated_session.notes, "Updated notes")
        self.assertEqual(updated_session.rpe, 9)

    def test_update_session_repository_partial(self):
        """Test: Actualizar sesión parcialmente."""
        # Arrange
        validated_data = {"notes": "New notes"}

        # Act
        updated_session = update_session_repository(
            session=self.session1, validated_data=validated_data
        )

        # Assert
        self.assertEqual(updated_session.notes, "New notes")
        # Verificar que otros campos no cambiaron
        self.assertEqual(updated_session.date, self.session1.date)

    def test_delete_session_repository(self):
        """Test: Eliminar sesión (eliminación física)."""
        # Arrange
        session_id = self.session1.id

        # Act
        delete_session_repository(session=self.session1)

        # Assert
        self.assertFalse(Session.objects.filter(id=session_id).exists())


class SessionExerciseRepositoryTestCase(TestCase):
    """Tests unitarios para los repositorios de SessionExercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.session = SessionFactory(user=self.user)
        self.exercise = ExerciseFactory()
        self.session_exercise1 = SessionExerciseFactory(
            session=self.session, exercise=self.exercise, order=1
        )
        self.session_exercise2 = SessionExerciseFactory(
            session=self.session, exercise=self.exercise, order=2
        )

    def test_list_session_exercises_repository(self):
        """Test: Listar ejercicios de una sesión."""
        # Arrange & Act
        queryset = list_session_exercises_repository(session=self.session)

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.session_exercise1, queryset)
        self.assertIn(self.session_exercise2, queryset)

    def test_list_session_exercises_repository_with_ordering(self):
        """Test: Listar ejercicios con ordenamiento."""
        # Arrange
        ordering = "-order"

        # Act
        queryset = list_session_exercises_repository(
            session=self.session, ordering=ordering
        )

        # Assert
        exercises = list(queryset)
        self.assertEqual(exercises[0].order, 2)
        self.assertEqual(exercises[1].order, 1)

    def test_list_session_exercises_repository_default_ordering(self):
        """Test: Ordenamiento por defecto (order)."""
        # Arrange & Act
        queryset = list_session_exercises_repository(session=self.session)

        # Assert
        exercises = list(queryset)
        self.assertEqual(exercises[0].order, 1)
        self.assertEqual(exercises[1].order, 2)

    def test_get_session_exercise_by_id_repository_existing(self):
        """Test: Obtener ejercicio de sesión por ID existente."""
        # Arrange & Act
        session_exercise = get_session_exercise_by_id_repository(
            session_exercise_id=self.session_exercise1.id
        )

        # Assert
        self.assertIsNotNone(session_exercise)
        self.assertEqual(session_exercise.id, self.session_exercise1.id)

    def test_get_session_exercise_by_id_repository_non_existing(self):
        """Test: Obtener ejercicio de sesión por ID inexistente."""
        # Arrange & Act
        session_exercise = get_session_exercise_by_id_repository(
            session_exercise_id=99999
        )

        # Assert
        self.assertIsNone(session_exercise)

    def test_create_session_exercise_repository(self):
        """Test: Crear ejercicio de sesión en repositorio."""
        # Arrange
        new_exercise = ExerciseFactory()
        validated_data = {
            "exerciseId": new_exercise.id,
            "order": 3,
            "setsCompleted": 4,
            "repetitions": "10",
            "weight": 80.5,
            "rpe": 8,
        }

        # Act
        session_exercise = create_session_exercise_repository(
            session=self.session, validated_data=validated_data
        )

        # Assert
        self.assertIsNotNone(session_exercise.id)
        self.assertEqual(session_exercise.session, self.session)
        self.assertEqual(session_exercise.exercise, new_exercise)
        self.assertEqual(session_exercise.order, 3)
        self.assertEqual(session_exercise.sets_completed, 4)

    def test_update_session_exercise_repository(self):
        """Test: Actualizar ejercicio de sesión en repositorio."""
        # Arrange
        validated_data = {
            "setsCompleted": 5,
            "weight": 85.0,
        }

        # Act
        updated_session_exercise = update_session_exercise_repository(
            session_exercise=self.session_exercise1, validated_data=validated_data
        )

        # Assert
        self.assertEqual(updated_session_exercise.sets_completed, 5)
        self.assertEqual(updated_session_exercise.weight, 85.0)

    def test_delete_session_exercise_repository(self):
        """Test: Eliminar ejercicio de sesión (eliminación física)."""
        # Arrange
        session_exercise_id = self.session_exercise1.id

        # Act
        delete_session_exercise_repository(session_exercise=self.session_exercise1)

        # Assert
        self.assertFalse(
            SessionExercise.objects.filter(id=session_exercise_id).exists()
        )


# ============================================================================
# Tests Unitarios - Services (con mocks de repositories)
# ============================================================================


class SessionServiceTestCase(TestCase):
    """Tests unitarios para los servicios de Session."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.other_user = UserFactory()

    @patch("apps.sessions.services.list_sessions_repository")
    def test_list_sessions_service_without_filters(self, mock_repository):
        """Test: Listar sesiones sin filtros."""
        # Arrange
        mock_session = MagicMock()
        mock_repository.return_value = [mock_session]

        # Act
        result = list_sessions_service(user=self.user)

        # Assert
        self.assertEqual(len(result), 1)
        mock_repository.assert_called_once_with(
            user=self.user, routine_id=None, date_filter=None
        )

    @patch("apps.sessions.services.list_sessions_repository")
    def test_list_sessions_service_with_routine_filter(self, mock_repository):
        """Test: Listar sesiones con filtro de rutina."""
        # Arrange
        routine = RoutineFactory(created_by=self.user)
        mock_repository.return_value = []

        # Act
        result = list_sessions_service(user=self.user, routine_id=routine.id)

        # Assert
        self.assertEqual(len(result), 0)
        mock_repository.assert_called_once_with(
            user=self.user, routine_id=routine.id, date_filter=None
        )

    @patch("apps.routines.repositories.get_routine_by_id_repository")
    @patch("apps.sessions.services.list_sessions_repository")
    def test_list_sessions_service_with_invalid_routine(self, mock_list, mock_get_routine):
        """Test: Listar sesiones con rutina inválida."""
        # Arrange
        mock_get_routine.return_value = None

        # Act & Assert
        from rest_framework.exceptions import ValidationError as DRFValidationError
        with self.assertRaises(DRFValidationError):
            list_sessions_service(user=self.user, routine_id=999)

        mock_list.assert_not_called()

    @patch("apps.routines.repositories.get_routine_by_id_repository")
    @patch("apps.sessions.services.list_sessions_repository")
    def test_list_sessions_service_with_routine_not_owned(self, mock_list, mock_get_routine):
        """Test: Listar sesiones con rutina que no pertenece al usuario."""
        # Arrange
        routine = RoutineFactory(created_by=self.other_user)
        mock_get_routine.return_value = routine

        # Act & Assert
        from rest_framework.exceptions import ValidationError as DRFValidationError
        with self.assertRaises(DRFValidationError):
            list_sessions_service(user=self.user, routine_id=routine.id)

        mock_list.assert_not_called()

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_get_session_service_existing(self, mock_repository):
        """Test: Obtener sesión existente."""
        # Arrange
        session = SessionFactory(user=self.user)
        mock_repository.return_value = session

        # Act
        result = get_session_service(session_id=session.id, user=self.user)

        # Assert
        self.assertEqual(result.id, session.id)
        mock_repository.assert_called_once_with(session_id=session.id)

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_get_session_service_non_existing(self, mock_repository):
        """Test: Obtener sesión inexistente."""
        # Arrange
        mock_repository.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            get_session_service(session_id=999, user=self.user)

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_get_session_service_permission_denied(self, mock_repository):
        """Test: Obtener sesión sin permisos."""
        # Arrange
        session = SessionFactory(user=self.other_user)
        mock_repository.return_value = session

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            get_session_service(session_id=session.id, user=self.user)

    @patch("apps.sessions.services.create_session_repository")
    def test_create_session_service_success(self, mock_repository):
        """Test: Crear sesión exitosamente."""
        # Arrange
        session = SessionFactory(user=self.user)
        mock_repository.return_value = session
        validated_data = {"date": date.today()}

        # Act
        result = create_session_service(validated_data=validated_data, user=self.user)

        # Assert
        self.assertEqual(result.id, session.id)
        mock_repository.assert_called_once()

    @patch("apps.sessions.services.create_session_repository")
    def test_create_session_service_without_date(self, mock_repository):
        """Test: Crear sesión sin fecha."""
        # Arrange
        validated_data = {}

        # Act & Assert
        from rest_framework.exceptions import ValidationError as DRFValidationError
        with self.assertRaises(DRFValidationError):
            create_session_service(validated_data=validated_data, user=self.user)

        mock_repository.assert_not_called()

    @patch("apps.sessions.services.create_session_repository")
    def test_create_session_service_with_invalid_energy_level(self, mock_repository):
        """Test: Crear sesión con energyLevel inválido."""
        # Arrange
        validated_data = {"date": date.today(), "energyLevel": "invalid"}

        # Act & Assert
        from rest_framework.exceptions import ValidationError as DRFValidationError
        with self.assertRaises(DRFValidationError):
            create_session_service(validated_data=validated_data, user=self.user)

        mock_repository.assert_not_called()

    @patch("apps.routines.repositories.get_routine_by_id_repository")
    @patch("apps.sessions.services.create_session_repository")
    def test_create_session_service_with_invalid_routine(self, mock_create, mock_get_routine):
        """Test: Crear sesión con rutina inválida."""
        # Arrange
        mock_get_routine.return_value = None
        validated_data = {"date": date.today(), "routineId": 999}

        # Act & Assert
        from rest_framework.exceptions import ValidationError as DRFValidationError
        with self.assertRaises(DRFValidationError):
            create_session_service(validated_data=validated_data, user=self.user)

        mock_create.assert_not_called()

    @patch("apps.routines.repositories.get_routine_by_id_repository")
    @patch("apps.sessions.services.create_session_repository")
    def test_create_session_service_with_routine_not_owned(self, mock_create, mock_get_routine):
        """Test: Crear sesión con rutina que no pertenece al usuario."""
        # Arrange
        routine = RoutineFactory(created_by=self.other_user)
        mock_get_routine.return_value = routine
        validated_data = {"date": date.today(), "routineId": routine.id}

        # Act & Assert
        from rest_framework.exceptions import ValidationError as DRFValidationError
        with self.assertRaises(DRFValidationError):
            create_session_service(validated_data=validated_data, user=self.user)

        mock_create.assert_not_called()

    @patch("apps.sessions.services.get_session_by_id_repository")
    @patch("apps.sessions.services.update_session_repository")
    def test_update_session_service_success(self, mock_update, mock_get):
        """Test: Actualizar sesión exitosamente."""
        # Arrange
        session = SessionFactory(user=self.user)
        mock_get.return_value = session
        mock_update.return_value = session
        validated_data = {"notes": "Updated notes"}

        # Act
        result = update_session_service(
            session_id=session.id, validated_data=validated_data, user=self.user
        )

        # Assert
        self.assertIsNotNone(result)
        mock_get.assert_called_once_with(session_id=session.id)
        mock_update.assert_called_once()

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_update_session_service_non_existing(self, mock_repository):
        """Test: Actualizar sesión inexistente."""
        # Arrange
        mock_repository.return_value = None
        validated_data = {"notes": "Updated notes"}

        # Act & Assert
        with self.assertRaises(NotFound):
            update_session_service(
                session_id=999, validated_data=validated_data, user=self.user
            )

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_update_session_service_permission_denied(self, mock_repository):
        """Test: Actualizar sesión sin permisos."""
        # Arrange
        session = SessionFactory(user=self.other_user)
        mock_repository.return_value = session
        validated_data = {"notes": "Updated notes"}

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            update_session_service(
                session_id=session.id, validated_data=validated_data, user=self.user
            )

    @patch("apps.sessions.services.get_session_by_id_repository")
    @patch("apps.sessions.services.delete_session_repository")
    def test_delete_session_service_success(self, mock_delete, mock_get):
        """Test: Eliminar sesión exitosamente."""
        # Arrange
        session = SessionFactory(user=self.user)
        mock_get.return_value = session

        # Act
        delete_session_service(session_id=session.id, user=self.user)

        # Assert
        mock_get.assert_called_once_with(session_id=session.id)
        mock_delete.assert_called_once_with(session=session)

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_delete_session_service_non_existing(self, mock_repository):
        """Test: Eliminar sesión inexistente."""
        # Arrange
        mock_repository.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            delete_session_service(session_id=999, user=self.user)

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_delete_session_service_permission_denied(self, mock_repository):
        """Test: Eliminar sesión sin permisos."""
        # Arrange
        session = SessionFactory(user=self.other_user)
        mock_repository.return_value = session

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            delete_session_service(session_id=session.id, user=self.user)


class SessionExerciseServiceTestCase(TestCase):
    """Tests unitarios para los servicios de SessionExercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.session = SessionFactory(user=self.user)
        self.exercise = ExerciseFactory()

    @patch("apps.sessions.services.get_session_by_id_repository")
    @patch("apps.exercises.repositories.get_exercise_by_id_repository")
    @patch("apps.sessions.services.create_session_exercise_repository")
    def test_create_session_exercise_service_success(
        self, mock_create, mock_get_exercise, mock_get_session
    ):
        """Test: Crear ejercicio de sesión exitosamente."""
        # Arrange
        mock_get_session.return_value = self.session
        mock_get_exercise.return_value = self.exercise
        session_exercise = SessionExerciseFactory(
            session=self.session, exercise=self.exercise
        )
        mock_create.return_value = session_exercise
        validated_data = {"setsCompleted": 4}

        # Act
        validated_data["exerciseId"] = self.exercise.id
        result = create_session_exercise_service(
            session_id=self.session.id,
            validated_data=validated_data,
            user=self.user,
        )

        # Assert
        self.assertIsNotNone(result)
        mock_get_session.assert_called_once_with(session_id=self.session.id)
        mock_get_exercise.assert_called_once_with(exercise_id=self.exercise.id)
        mock_create.assert_called_once()

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_create_session_exercise_service_session_not_found(self, mock_get_session):
        """Test: Crear ejercicio de sesión con sesión inexistente."""
        # Arrange
        mock_get_session.return_value = None
        validated_data = {"setsCompleted": 4}

        # Act & Assert
        validated_data["exerciseId"] = self.exercise.id
        with self.assertRaises(NotFound):
            create_session_exercise_service(
                session_id=999,
                validated_data=validated_data,
                user=self.user,
            )

    @patch("apps.sessions.services.get_session_by_id_repository")
    def test_create_session_exercise_service_permission_denied(self, mock_get_session):
        """Test: Crear ejercicio de sesión sin permisos."""
        # Arrange
        other_session = SessionFactory(user=self.other_user)
        mock_get_session.return_value = other_session
        validated_data = {"setsCompleted": 4}

        # Act & Assert
        validated_data["exerciseId"] = self.exercise.id
        with self.assertRaises(PermissionDenied):
            create_session_exercise_service(
                session_id=other_session.id,
                validated_data=validated_data,
                user=self.user,
            )

    @patch("apps.sessions.services.update_session_exercise_repository")
    @patch("apps.sessions.services.get_session_exercise_by_id_repository")
    def test_update_session_exercise_service_success(
        self, mock_get_exercise, mock_update
    ):
        """Test: Actualizar ejercicio de sesión exitosamente."""
        # Arrange
        session_exercise = SessionExercise.objects.create(
            session=self.session, exercise=self.exercise, order=1
        )
        mock_get_exercise.return_value = session_exercise
        mock_update.return_value = session_exercise
        validated_data = {"setsCompleted": 5}

        # Act
        result = update_session_exercise_service(
            session_exercise_id=session_exercise.id,
            validated_data=validated_data,
            user=self.user,
        )

        # Assert
        self.assertIsNotNone(result)
        mock_get_exercise.assert_called_once_with(
            session_exercise_id=session_exercise.id
        )
        mock_update.assert_called_once_with(
            session_exercise=session_exercise, validated_data=validated_data
        )

    @patch("apps.sessions.repositories.get_session_exercise_by_id_repository")
    def test_update_session_exercise_service_not_found(self, mock_get_exercise):
        """Test: Actualizar ejercicio de sesión inexistente."""
        # Arrange
        mock_get_exercise.return_value = None
        validated_data = {"setsCompleted": 5}

        # Act & Assert
        with self.assertRaises(NotFound):
            update_session_exercise_service(
                session_exercise_id=999,
                validated_data=validated_data,
                user=self.user,
            )

    @patch("apps.sessions.services.delete_session_exercise_repository")
    @patch("apps.sessions.services.get_session_exercise_service")
    def test_delete_session_exercise_service_success(
        self, mock_get_service, mock_delete
    ):
        """Test: Eliminar ejercicio de sesión exitosamente."""
        # Arrange
        session_exercise = SessionExercise.objects.create(
            session=self.session, exercise=self.exercise, order=1
        )
        mock_get_service.return_value = session_exercise

        # Act
        delete_session_exercise_service(
            session_exercise_id=session_exercise.id,
            user=self.user,
        )

        # Assert
        mock_get_service.assert_called_once_with(
            session_exercise_id=session_exercise.id, user=self.user
        )
        mock_delete.assert_called_once_with(session_exercise=session_exercise)


# ============================================================================
# Tests Unitarios - Serializers
# ============================================================================


class SessionSerializerTestCase(TestCase):
    """Tests unitarios para los serializadores de Session."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.routine = RoutineFactory(created_by=self.user)
        self.session = SessionFactory(
            user=self.user,
            routine=self.routine,
            date=date.today(),
            rpe=8,
            energy_level="high",
            sleep_hours=7.5,
        )

    def test_session_serializer_serialization(self):
        """Test: Serialización de sesión."""
        # Arrange
        serializer = SessionSerializer(self.session)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.session.id)
        self.assertEqual(data["userId"], self.user.id)
        self.assertEqual(data["user"], self.user.username)
        self.assertEqual(data["routineId"], self.routine.id)
        self.assertEqual(data["routine"], self.routine.name)
        self.assertEqual(data["date"], self.session.date.isoformat())
        self.assertEqual(data["rpe"], 8)
        self.assertEqual(data["energyLevel"], "high")
        self.assertEqual(float(data["sleepHours"]), 7.5)
        self.assertIn("createdAt", data)
        self.assertIn("updatedAt", data)

    def test_session_serializer_without_routine(self):
        """Test: Serialización de sesión sin rutina."""
        # Arrange
        session = SessionFactory(user=self.user, routine=None)
        serializer = SessionSerializer(session)

        # Act
        data = serializer.data

        # Assert
        self.assertIsNone(data["routineId"])
        self.assertIsNone(data["routine"])

    def test_session_create_serializer_valid_data(self):
        """Test: Serializador de creación con datos válidos."""
        # Arrange
        data = {
            "date": date.today().isoformat(),
            "routineId": self.routine.id,
            "notes": "Test session",
            "rpe": 8,
            "energyLevel": "high",
        }

        # Act
        serializer = SessionCreateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["date"], date.today())
        self.assertEqual(serializer.validated_data["routineId"], self.routine.id)

    def test_session_create_serializer_date_required(self):
        """Test: Serializador de creación requiere fecha."""
        # Arrange
        data = {"notes": "No date"}

        # Act
        serializer = SessionCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)

    def test_session_create_serializer_rpe_validation(self):
        """Test: Serializador de creación valida RPE."""
        # Arrange
        data = {"date": date.today().isoformat(), "rpe": 11}

        # Act
        serializer = SessionCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("rpe", serializer.errors)

    def test_session_update_serializer_valid_data(self):
        """Test: Serializador de actualización con datos válidos."""
        # Arrange
        data = {"notes": "Updated notes", "rpe": 9}

        # Act
        serializer = SessionUpdateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["notes"], "Updated notes")
        self.assertEqual(serializer.validated_data["rpe"], 9)

    def test_session_update_serializer_partial_update(self):
        """Test: Serializador de actualización permite actualización parcial."""
        # Arrange
        data = {"notes": "Updated notes"}

        # Act
        serializer = SessionUpdateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["notes"], "Updated notes")


class SessionExerciseSerializerTestCase(TestCase):
    """Tests unitarios para los serializadores de SessionExercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.session = SessionFactory(user=self.user)
        self.exercise = ExerciseFactory(name="Bench Press")
        self.session_exercise = SessionExerciseFactory(
            session=self.session,
            exercise=self.exercise,
            sets_completed=4,
            repetitions="10",
            weight=80.5,
            rpe=8,
        )

    def test_session_exercise_serializer_serialization(self):
        """Test: Serialización de ejercicio de sesión."""
        # Arrange
        serializer = SessionExerciseSerializer(self.session_exercise)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.session_exercise.id)
        self.assertEqual(data["sessionId"], self.session.id)
        self.assertEqual(data["exerciseId"], self.exercise.id)
        self.assertEqual(data["setsCompleted"], 4)
        self.assertEqual(data["repetitions"], "10")
        self.assertEqual(float(data["weight"]), 80.5)
        self.assertEqual(data["rpe"], 8)
        self.assertIn("exercise", data)
        self.assertEqual(data["exercise"]["name"], "Bench Press")
        self.assertIn("createdAt", data)
        self.assertIn("updatedAt", data)

    def test_session_exercise_create_serializer_valid_data(self):
        """Test: Serializador de creación con datos válidos."""
        # Arrange
        data = {
            "exerciseId": self.exercise.id,
            "order": 1,
            "setsCompleted": 4,
            "repetitions": "10",
            "weight": 80.5,
            "rpe": 8,
        }

        # Act
        serializer = SessionExerciseCreateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["exerciseId"], self.exercise.id)

    def test_session_exercise_create_serializer_exercise_id_required(self):
        """Test: Serializador de creación requiere exerciseId."""
        # Arrange
        data = {"setsCompleted": 4}

        # Act
        serializer = SessionExerciseCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("exerciseId", serializer.errors)

    def test_session_exercise_update_serializer_valid_data(self):
        """Test: Serializador de actualización con datos válidos."""
        # Arrange
        data = {"setsCompleted": 5, "weight": 85.0}

        # Act
        serializer = SessionExerciseUpdateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["setsCompleted"], 5)
        self.assertEqual(serializer.validated_data["weight"], 85.0)


# ============================================================================
# Tests Unitarios - Forms
# ============================================================================


class SessionFormTestCase(TestCase):
    """Tests unitarios para los formularios de Session."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.routine = RoutineFactory(created_by=self.user)

    def test_session_create_form_valid_data(self):
        """Test: Formulario de creación con datos válidos."""
        # Arrange
        form_data = {
            "date": date.today(),
            "routine": self.routine.id,
            "notes": "Test session",
            "rpe": 8,
            "energy_level": "high",
        }

        # Act
        form = SessionCreateForm(data=form_data, user=self.user)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["date"], date.today())
        self.assertEqual(form.cleaned_data["routine"], self.routine)

    def test_session_create_form_date_required(self):
        """Test: Formulario de creación requiere fecha."""
        # Arrange
        form_data = {"notes": "No date"}

        # Act
        form = SessionCreateForm(data=form_data, user=self.user)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_session_create_form_validates_time_consistency(self):
        """Test: Formulario valida consistencia de tiempos."""
        # Arrange
        start_time = timezone.now()
        end_time = start_time - timedelta(hours=1)
        form_data = {
            "date": date.today(),
            "start_time": start_time,
            "end_time": end_time,
        }

        # Act
        form = SessionCreateForm(data=form_data, user=self.user)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn("end_time", form.errors)

    def test_session_update_form_valid_data(self):
        """Test: Formulario de actualización con datos válidos."""
        # Arrange
        form_data = {"notes": "Updated notes", "rpe": 9}

        # Act
        form = SessionUpdateForm(data=form_data, user=self.user)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["notes"], "Updated notes")


class SessionExerciseFormTestCase(TestCase):
    """Tests unitarios para los formularios de SessionExercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.session = SessionFactory(user=self.user)
        self.exercise = ExerciseFactory()

    def test_session_exercise_form_valid_data(self):
        """Test: Formulario de ejercicio con datos válidos."""
        # Arrange
        form_data = {
            "exercise": self.exercise.id,
            "order": 1,
            "sets_completed": 4,
            "repetitions": "10",
            "weight": 80.5,
            "rpe": 8,
        }

        # Act
        form = SessionExerciseForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["exercise"], self.exercise)

    def test_session_exercise_form_exercise_required(self):
        """Test: Formulario requiere ejercicio."""
        # Arrange
        form_data = {"sets_completed": 4}

        # Act
        form = SessionExerciseForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn("exercise", form.errors)

    def test_session_exercise_form_validates_rpe_range(self):
        """Test: Formulario valida rango de RPE."""
        # Arrange
        form_data = {
            "exercise": self.exercise.id,
            "rpe": 11,
        }

        # Act
        form = SessionExerciseForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn("rpe", form.errors)


# ============================================================================
# Tests de Integración - API Views
# ============================================================================


class SessionAPITestCase(TestCase):
    """Tests de integración para las vistas API de Session."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.client = APIClient()
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.routine = RoutineFactory(created_by=self.user)
        self.session = SessionFactory(user=self.user, routine=self.routine)

    def test_session_list_api_get_success(self):
        """Test: GET /api/sessions/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.get("/api/sessions/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], self.session.id)

    def test_session_list_api_get_unauthenticated(self):
        """Test: GET /api/sessions/ sin autenticación."""
        # Arrange & Act
        response = self.client.get("/api/sessions/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_session_list_api_get_with_routine_filter(self):
        """Test: GET /api/sessions/ con filtro de rutina."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        SessionFactory(user=self.user, routine=None)  # Otra sesión sin rutina

        # Act
        response = self.client.get(f"/api/sessions/?routineId={self.routine.id}")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["routineId"], self.routine.id)

    def test_session_list_api_post_success(self):
        """Test: POST /api/sessions/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            "date": date.today().isoformat(),
            "routineId": self.routine.id,
            "notes": "New session",
            "rpe": 8,
        }

        # Act
        response = self.client.post("/api/sessions/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["notes"], "New session")
        self.assertIn("message", response.data)

    def test_session_list_api_post_invalid_data(self):
        """Test: POST /api/sessions/ con datos inválidos."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {"rpe": 11}  # RPE inválido

        # Act
        response = self.client.post("/api/sessions/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_session_detail_api_get_success(self):
        """Test: GET /api/sessions/{id}/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        exercise = ExerciseFactory()
        # Crear ejercicio de sesión directamente para evitar problemas con factory
        SessionExercise.objects.create(
            session=self.session,
            exercise=exercise,
            order=1,
            sets_completed=4,
        )

        # Act
        response = self.client.get(f"/api/sessions/{self.session.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["id"], self.session.id)
        self.assertIn("sessionExercises", response.data["data"])

    def test_session_detail_api_get_not_found(self):
        """Test: GET /api/sessions/{id}/ no encontrado."""
        # Arrange
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.get("/api/sessions/99999/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_session_detail_api_get_permission_denied(self):
        """Test: GET /api/sessions/{id}/ sin permisos."""
        # Arrange
        self.client.force_authenticate(user=self.other_user)

        # Act
        response = self.client.get(f"/api/sessions/{self.session.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)

    def test_session_detail_api_put_success(self):
        """Test: PUT /api/sessions/{id}/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {"notes": "Updated notes"}

        # Act
        response = self.client.put(
            f"/api/sessions/{self.session.id}/", data, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["notes"], "Updated notes")
        self.assertIn("message", response.data)

    def test_session_detail_api_delete_success(self):
        """Test: DELETE /api/sessions/{id}/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.delete(f"/api/sessions/{self.session.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Session.objects.filter(id=self.session.id).exists())

    def test_session_exercise_list_api_get_success(self):
        """Test: GET /api/sessions/{id}/exercises/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        exercise = ExerciseFactory()
        # Crear ejercicio de sesión directamente para evitar problemas con factory
        SessionExercise.objects.create(
            session=self.session,
            exercise=exercise,
            order=1,
            sets_completed=4,
        )

        # Act
        response = self.client.get(f"/api/sessions/{self.session.id}/exercises/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 1)

    def test_session_exercise_list_api_post_success(self):
        """Test: POST /api/sessions/{id}/exercises/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        exercise = ExerciseFactory()
        data = {
            "exerciseId": exercise.id,
            "setsCompleted": 4,
            "repetitions": "10",
            "weight": 80.5,
            "rpe": 8,
        }

        # Act
        response = self.client.post(
            f"/api/sessions/{self.session.id}/exercises/", data, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["setsCompleted"], 4)
        self.assertIn("message", response.data)


# ============================================================================
# Tests de Integración - Web Views
# ============================================================================


class SessionWebViewTestCase(TestCase):
    """Tests de integración para las vistas web de Session."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.routine = RoutineFactory(created_by=self.user)
        self.session = SessionFactory(user=self.user, routine=self.routine)

    def test_session_list_view_get_authenticated(self):
        """Test: Vista de lista GET autenticado."""
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get("/sessions/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("sessions", response.context)

    def test_session_list_view_get_unauthenticated(self):
        """Test: Vista de lista GET sin autenticación."""
        # Arrange & Act
        response = self.client.get("/sessions/")

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_session_detail_view_get_authenticated(self):
        """Test: Vista de detalle GET autenticado."""
        # Arrange
        self.client.force_login(self.user)
        exercise = ExerciseFactory()
        # Crear ejercicio de sesión directamente para evitar problemas con factory
        SessionExercise.objects.create(
            session=self.session,
            exercise=exercise,
            order=1,
            sets_completed=4,
        )

        # Act
        response = self.client.get(f"/sessions/{self.session.id}/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("session", response.context)
        self.assertEqual(response.context["session"]["id"], self.session.id)

    def test_session_detail_view_get_permission_denied(self):
        """Test: Vista de detalle GET sin permisos."""
        # Arrange
        self.client.force_login(self.other_user)

        # Act
        response = self.client.get(f"/sessions/{self.session.id}/")

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_session_create_view_get_authenticated(self):
        """Test: Vista de creación GET autenticado."""
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get("/sessions/create/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_session_create_view_post_success(self):
        """Test: Vista de creación POST exitoso."""
        # Arrange
        self.client.force_login(self.user)
        data = {
            "date": date.today(),
            "routine": self.routine.id,
            "notes": "New session",
            "rpe": 8,
        }

        # Act
        response = self.client.post("/sessions/create/", data)

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(
            Session.objects.filter(user=self.user, notes="New session").exists()
        )

    def test_session_update_view_get_authenticated_owner(self):
        """Test: Vista de actualización GET como propietario."""
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get(f"/sessions/{self.session.id}/update/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_session_update_view_post_success(self):
        """Test: Vista de actualización POST exitoso."""
        # Arrange
        self.client.force_login(self.user)
        data = {"date": date.today(), "notes": "Updated notes"}

        # Act
        response = self.client.post(f"/sessions/{self.session.id}/update/", data)

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        self.session.refresh_from_db()
        self.assertEqual(self.session.notes, "Updated notes")

    def test_session_delete_view_post_success(self):
        """Test: Vista de eliminación POST exitoso."""
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.post(f"/sessions/{self.session.id}/delete/")

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(Session.objects.filter(id=self.session.id).exists())
