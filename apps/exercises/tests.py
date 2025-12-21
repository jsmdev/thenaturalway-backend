from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.test import APIClient

from apps.exercises.factories import (
    EquipmentFactory,
    MovementTypeFactory,
    MuscleGroupFactory,
)
from apps.exercises.forms import ExerciseCreateForm, ExerciseUpdateForm
from apps.exercises.models import Exercise, MuscleGroup
from apps.exercises.repositories import (
    create_exercise_repository,
    delete_exercise_repository,
    get_exercise_by_id_repository,
    list_exercises_repository,
    update_exercise_repository,
)
from apps.exercises.serializers import (
    ExerciseCreateSerializer,
    ExerciseSerializer,
    ExerciseUpdateSerializer,
)
from apps.exercises.services import (
    create_exercise_service,
    delete_exercise_service,
    get_exercise_service,
    list_exercises_service,
    update_exercise_service,
)

User = get_user_model()


# ============================================================================
# Tests Unitarios - Models
# ============================================================================


class ExerciseModelTestCase(TestCase):
    """Tests unitarios para el modelo Exercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.movement_type = MovementTypeFactory(name="push", display_name="Push")
        self.muscle_group = MuscleGroupFactory(name="chest", display_name="Chest")
        self.equipment = EquipmentFactory(name="barbell", display_name="Barbell")

    def test_exercise_creation_with_minimal_data(self):
        """Test: Crear ejercicio con datos mínimos."""
        # Arrange
        exercise_data = {"name": "Push Up"}

        # Act
        exercise = Exercise.objects.create(**exercise_data)

        # Assert
        self.assertEqual(exercise.name, "Push Up")
        self.assertTrue(exercise.is_active)
        self.assertIsNone(exercise.description)
        self.assertIsNone(exercise.created_by)

    def test_exercise_creation_with_all_fields(self):
        """Test: Crear ejercicio con todos los campos."""
        # Arrange - Crear grupos musculares secundarios para referencia
        MuscleGroupFactory(name="shoulders", display_name="Shoulders")
        MuscleGroupFactory(name="arms", display_name="Arms")
        exercise_data = {
            "name": "Bench Press",
            "description": "Classic chest exercise",
            "movement_type": self.movement_type,
            "primary_muscle_group": self.muscle_group,
            "secondary_muscle_groups": ["shoulders", "arms"],
            "equipment": self.equipment,
            "difficulty": "intermediate",
            "instructions": "Lie on bench and press",
            "image_url": "https://example.com/image.jpg",
            "video_url": "https://example.com/video.mp4",
            "is_active": True,
            "created_by": self.user,
        }

        # Act
        exercise = Exercise.objects.create(**exercise_data)

        # Assert
        self.assertEqual(exercise.name, "Bench Press")
        self.assertEqual(exercise.description, "Classic chest exercise")
        self.assertEqual(exercise.movement_type, self.movement_type)
        self.assertEqual(exercise.primary_muscle_group, self.muscle_group)
        self.assertEqual(exercise.secondary_muscle_groups, ["shoulders", "arms"])
        self.assertEqual(exercise.equipment, self.equipment)
        self.assertEqual(exercise.difficulty, "intermediate")
        self.assertEqual(exercise.instructions, "Lie on bench and press")
        self.assertEqual(exercise.image_url, "https://example.com/image.jpg")
        self.assertEqual(exercise.video_url, "https://example.com/video.mp4")
        self.assertTrue(exercise.is_active)
        self.assertEqual(exercise.created_by, self.user)

    def test_exercise_str_representation(self):
        """Test: Representación string del ejercicio."""
        # Arrange
        exercise = Exercise.objects.create(name="Squat")

        # Act
        str_repr = str(exercise)

        # Assert
        self.assertEqual(str_repr, "Squat")

    def test_exercise_choices_validation(self):
        """Test: Validación de choices válidos."""
        # Arrange & Act
        exercise = Exercise.objects.create(
            name="Test Exercise",
            movement_type=self.movement_type,
            primary_muscle_group=self.muscle_group,
            equipment=self.equipment,
            difficulty="beginner",
        )

        # Assert
        self.assertEqual(exercise.movement_type, self.movement_type)
        self.assertEqual(exercise.primary_muscle_group, self.muscle_group)
        self.assertEqual(exercise.equipment, self.equipment)
        self.assertEqual(exercise.difficulty, "beginner")

    def test_exercise_default_is_active(self):
        """Test: Valor por defecto de is_active."""
        # Arrange & Act
        exercise = Exercise.objects.create(name="Test Exercise")

        # Assert
        self.assertTrue(exercise.is_active)

    def test_exercise_created_at_auto_now_add(self):
        """Test: created_at se establece automáticamente."""
        # Arrange & Act
        exercise = Exercise.objects.create(name="Test Exercise")

        # Assert
        self.assertIsNotNone(exercise.created_at)

    def test_exercise_updated_at_auto_now(self):
        """Test: updated_at se actualiza automáticamente."""
        # Arrange
        exercise = Exercise.objects.create(name="Test Exercise")
        original_updated_at = exercise.updated_at

        # Act
        exercise.name = "Updated Name"
        exercise.save()

        # Assert
        self.assertGreater(exercise.updated_at, original_updated_at)


# ============================================================================
# Tests Unitarios - Repositories
# ============================================================================


class ExerciseRepositoryTestCase(TestCase):
    """Tests unitarios para los repositorios de Exercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        # Crear opciones de configuración
        self.chest = MuscleGroupFactory(name="chest", display_name="Chest")
        self.back = MuscleGroupFactory(name="back", display_name="Back")
        self.bodyweight = EquipmentFactory(name="bodyweight", display_name="Bodyweight")
        self.barbell = EquipmentFactory(name="barbell", display_name="Barbell")

        self.exercise1 = Exercise.objects.create(
            name="Push Up",
            primary_muscle_group=self.chest,
            equipment=self.bodyweight,
            difficulty="beginner",
            is_active=True,
            created_by=self.user,
        )
        self.exercise2 = Exercise.objects.create(
            name="Bench Press",
            primary_muscle_group=self.chest,
            equipment=self.barbell,
            difficulty="intermediate",
            is_active=True,
        )
        self.exercise3 = Exercise.objects.create(
            name="Deadlift",
            primary_muscle_group=self.back,
            equipment=self.barbell,
            difficulty="advanced",
            is_active=False,
        )

    def test_list_exercises_repository_without_filters(self):
        """Test: Listar ejercicios sin filtros."""
        # Arrange & Act
        queryset = list_exercises_repository()

        # Assert
        self.assertEqual(queryset.count(), 3)
        self.assertIn(self.exercise1, queryset)
        self.assertIn(self.exercise2, queryset)
        self.assertIn(self.exercise3, queryset)

    def test_list_exercises_repository_with_primary_muscle_group_filter(self):
        """Test: Listar ejercicios filtrados por grupo muscular."""
        # Arrange
        filters = {"primaryMuscleGroup": "chest"}

        # Act
        queryset = list_exercises_repository(filters=filters)

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.exercise1, queryset)
        self.assertIn(self.exercise2, queryset)
        self.assertNotIn(self.exercise3, queryset)

    def test_list_exercises_repository_with_equipment_filter(self):
        """Test: Listar ejercicios filtrados por equipamiento."""
        # Arrange
        filters = {"equipment": "barbell"}

        # Act
        queryset = list_exercises_repository(filters=filters)

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.exercise2, queryset)
        self.assertIn(self.exercise3, queryset)
        self.assertNotIn(self.exercise1, queryset)

    def test_list_exercises_repository_with_difficulty_filter(self):
        """Test: Listar ejercicios filtrados por dificultad."""
        # Arrange
        filters = {"difficulty": "beginner"}

        # Act
        queryset = list_exercises_repository(filters=filters)

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.exercise1, queryset)

    def test_list_exercises_repository_with_is_active_filter(self):
        """Test: Listar ejercicios filtrados por is_active."""
        # Arrange
        filters = {"isActive": True}

        # Act
        queryset = list_exercises_repository(filters=filters)

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.exercise1, queryset)
        self.assertIn(self.exercise2, queryset)
        self.assertNotIn(self.exercise3, queryset)

    def test_list_exercises_repository_with_created_by_filter(self):
        """Test: Listar ejercicios filtrados por creador."""
        # Arrange
        filters = {"createdBy": self.user.id}

        # Act
        queryset = list_exercises_repository(filters=filters)

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.exercise1, queryset)

    def test_list_exercises_repository_with_search(self):
        """Test: Listar ejercicios con búsqueda."""
        # Arrange
        search = "Push"

        # Act
        queryset = list_exercises_repository(search=search)

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.exercise1, queryset)

    def test_list_exercises_repository_with_ordering(self):
        """Test: Listar ejercicios con ordenamiento."""
        # Arrange
        ordering = "-name"

        # Act
        queryset = list_exercises_repository(ordering=ordering)

        # Assert
        exercises = list(queryset)
        self.assertEqual(exercises[0].name, "Push Up")
        self.assertEqual(exercises[1].name, "Deadlift")
        self.assertEqual(exercises[2].name, "Bench Press")

    def test_list_exercises_repository_default_ordering(self):
        """Test: Ordenamiento por defecto (name)."""
        # Arrange & Act
        queryset = list_exercises_repository()

        # Assert
        exercises = list(queryset)
        self.assertEqual(exercises[0].name, "Bench Press")
        self.assertEqual(exercises[1].name, "Deadlift")
        self.assertEqual(exercises[2].name, "Push Up")

    def test_get_exercise_by_id_repository_existing(self):
        """Test: Obtener ejercicio por ID existente."""
        # Arrange & Act
        exercise = get_exercise_by_id_repository(exercise_id=self.exercise1.id)

        # Assert
        self.assertIsNotNone(exercise)
        self.assertEqual(exercise.id, self.exercise1.id)
        self.assertEqual(exercise.name, "Push Up")

    def test_get_exercise_by_id_repository_non_existing(self):
        """Test: Obtener ejercicio por ID inexistente."""
        # Arrange & Act
        exercise = get_exercise_by_id_repository(exercise_id=99999)

        # Assert
        self.assertIsNone(exercise)

    def test_create_exercise_repository(self):
        """Test: Crear ejercicio en repositorio."""
        # Arrange
        legs = MuscleGroupFactory(name="legs", display_name="Legs")
        barbell = EquipmentFactory(name="barbell", display_name="Barbell")
        validated_data = {
            "name": "Squat",
            "description": "Leg exercise",
            "primaryMuscleGroup": legs,
            "equipment": barbell,
            "difficulty": "intermediate",
        }

        # Act
        exercise = create_exercise_repository(validated_data=validated_data, user=self.user)

        # Assert
        self.assertIsNotNone(exercise.id)
        self.assertEqual(exercise.name, "Squat")
        self.assertEqual(exercise.description, "Leg exercise")
        self.assertEqual(exercise.primary_muscle_group, legs)
        self.assertEqual(exercise.equipment, barbell)
        self.assertEqual(exercise.difficulty, "intermediate")
        self.assertEqual(exercise.created_by, self.user)

    def test_create_exercise_repository_without_user(self):
        """Test: Crear ejercicio sin usuario."""
        # Arrange
        validated_data = {"name": "Squat"}

        # Act
        exercise = create_exercise_repository(validated_data=validated_data, user=None)

        # Assert
        self.assertIsNotNone(exercise.id)
        self.assertEqual(exercise.name, "Squat")
        self.assertIsNone(exercise.created_by)

    def test_update_exercise_repository(self):
        """Test: Actualizar ejercicio en repositorio."""
        # Arrange
        validated_data = {
            "name": "Updated Push Up",
            "description": "Updated description",
            "difficulty": "advanced",
        }

        # Act
        updated_exercise = update_exercise_repository(
            exercise=self.exercise1, validated_data=validated_data
        )

        # Assert
        self.assertEqual(updated_exercise.name, "Updated Push Up")
        self.assertEqual(updated_exercise.description, "Updated description")
        self.assertEqual(updated_exercise.difficulty, "advanced")

    def test_update_exercise_repository_partial(self):
        """Test: Actualizar ejercicio parcialmente."""
        # Arrange
        validated_data = {"name": "New Name"}

        # Act
        updated_exercise = update_exercise_repository(
            exercise=self.exercise1, validated_data=validated_data
        )

        # Assert
        self.assertEqual(updated_exercise.name, "New Name")
        self.assertEqual(updated_exercise.primary_muscle_group, self.chest)  # No cambió

    def test_delete_exercise_repository_soft_delete(self):
        """Test: Soft delete de ejercicio."""
        # Arrange
        self.assertTrue(self.exercise1.is_active)

        # Act
        deleted_exercise = delete_exercise_repository(exercise=self.exercise1)

        # Assert
        self.assertFalse(deleted_exercise.is_active)
        self.assertEqual(deleted_exercise.id, self.exercise1.id)
        # Verificar que el ejercicio aún existe en la BD
        self.assertTrue(Exercise.objects.filter(id=self.exercise1.id).exists())


# ============================================================================
# Tests Unitarios - Services (con mocks de repositories)
# ============================================================================


class ExerciseServiceTestCase(TestCase):
    """Tests unitarios para los servicios de Exercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    @patch("apps.exercises.services.list_exercises_repository")
    def test_list_exercises_service_without_filters(self, mock_repository):
        """Test: Listar ejercicios sin filtros."""
        # Arrange
        mock_exercise = MagicMock()
        mock_exercise.id = 1
        mock_exercise.name = "Test Exercise"
        mock_repository.return_value = [mock_exercise]

        # Act
        result = list_exercises_service()

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Test Exercise")
        mock_repository.assert_called_once_with(filters=None, search=None, ordering=None)

    @patch("apps.exercises.services.list_exercises_repository")
    def test_list_exercises_service_with_valid_filters(self, mock_repository):
        """Test: Listar ejercicios con filtros válidos."""
        # Arrange
        mock_exercise = MagicMock()
        mock_repository.return_value = [mock_exercise]
        filters = {
            "primaryMuscleGroup": "chest",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "isActive": True,
        }

        # Act
        result = list_exercises_service(filters=filters)

        # Assert
        self.assertEqual(len(result), 1)
        mock_repository.assert_called_once()

    @patch("apps.exercises.services.list_exercises_repository")
    def test_list_exercises_service_with_invalid_primary_muscle_group(self, mock_repository):
        """Test: Listar ejercicios con grupo muscular inválido."""
        # Arrange
        filters = {"primaryMuscleGroup": "invalid_group"}

        # Act & Assert
        with self.assertRaises(ValidationError):
            list_exercises_service(filters=filters)

        mock_repository.assert_not_called()

    @patch("apps.exercises.services.list_exercises_repository")
    def test_list_exercises_service_with_invalid_equipment(self, mock_repository):
        """Test: Listar ejercicios con equipamiento inválido."""
        # Arrange
        filters = {"equipment": "invalid_equipment"}

        # Act & Assert
        with self.assertRaises(ValidationError):
            list_exercises_service(filters=filters)

        mock_repository.assert_not_called()

    @patch("apps.exercises.services.list_exercises_repository")
    def test_list_exercises_service_with_invalid_difficulty(self, mock_repository):
        """Test: Listar ejercicios con dificultad inválida."""
        # Arrange
        filters = {"difficulty": "invalid_difficulty"}

        # Act & Assert
        with self.assertRaises(ValidationError):
            list_exercises_service(filters=filters)

        mock_repository.assert_not_called()

    @patch("apps.exercises.services.list_exercises_repository")
    def test_list_exercises_service_with_invalid_is_active(self, mock_repository):
        """Test: Listar ejercicios con isActive inválido."""
        # Arrange
        filters = {"isActive": "maybe"}

        # Act & Assert
        with self.assertRaises(ValidationError):
            list_exercises_service(filters=filters)

        mock_repository.assert_not_called()

    @patch("apps.exercises.services.list_exercises_repository")
    def test_list_exercises_service_with_invalid_created_by(self, mock_repository):
        """Test: Listar ejercicios con createdBy inválido."""
        # Arrange
        filters = {"createdBy": "not_a_number"}

        # Act & Assert
        with self.assertRaises(ValidationError):
            list_exercises_service(filters=filters)

        mock_repository.assert_not_called()

    @patch("apps.exercises.services.get_exercise_by_id_repository")
    def test_get_exercise_service_existing(self, mock_repository):
        """Test: Obtener ejercicio existente."""
        # Arrange
        mock_exercise = MagicMock()
        mock_exercise.id = 1
        mock_exercise.name = "Test Exercise"
        mock_repository.return_value = mock_exercise

        # Act
        result = get_exercise_service(exercise_id=1)

        # Assert
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Test Exercise")
        mock_repository.assert_called_once_with(exercise_id=1)

    @patch("apps.exercises.services.get_exercise_by_id_repository")
    def test_get_exercise_service_non_existing(self, mock_repository):
        """Test: Obtener ejercicio inexistente."""
        # Arrange
        mock_repository.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            get_exercise_service(exercise_id=999)

        mock_repository.assert_called_once_with(exercise_id=999)

    @patch("apps.exercises.services.create_exercise_repository")
    def test_create_exercise_service_success(self, mock_repository):
        """Test: Crear ejercicio exitosamente."""
        # Arrange
        mock_exercise = Exercise.objects.create(name="Test Exercise")
        mock_repository.return_value = mock_exercise
        validated_data = {"name": "Test Exercise", "primaryMuscleGroup": "chest"}

        # Act
        result = create_exercise_service(validated_data=validated_data, user=self.user)

        # Assert
        self.assertEqual(result.name, "Test Exercise")
        mock_repository.assert_called_once()

    @patch("apps.exercises.services.create_exercise_repository")
    def test_create_exercise_service_without_name(self, mock_repository):
        """Test: Crear ejercicio sin nombre."""
        # Arrange
        validated_data = {}

        # Act & Assert
        with self.assertRaises(ValidationError):
            create_exercise_service(validated_data=validated_data, user=self.user)

        mock_repository.assert_not_called()

    @patch("apps.exercises.services.create_exercise_repository")
    def test_create_exercise_service_with_invalid_movement_type(self, mock_repository):
        """Test: Crear ejercicio con movementType inválido."""
        # Arrange
        validated_data = {"name": "Test", "movementType": "invalid"}

        # Act & Assert
        with self.assertRaises(ValidationError):
            create_exercise_service(validated_data=validated_data, user=self.user)

        mock_repository.assert_not_called()

    @patch("apps.exercises.services.create_exercise_repository")
    def test_create_exercise_service_with_invalid_secondary_muscle_groups(self, mock_repository):
        """Test: Crear ejercicio con secondaryMuscleGroups inválido."""
        # Arrange
        validated_data = {
            "name": "Test",
            "secondaryMuscleGroups": "not_a_list",
        }

        # Act & Assert
        with self.assertRaises(ValidationError):
            create_exercise_service(validated_data=validated_data, user=self.user)

        mock_repository.assert_not_called()

    @patch("apps.exercises.services.get_exercise_by_id_repository")
    @patch("apps.exercises.services.update_exercise_repository")
    def test_update_exercise_service_success(self, mock_update, mock_get):
        """Test: Actualizar ejercicio exitosamente."""
        # Arrange
        exercise = Exercise.objects.create(name="Original", created_by=self.user)
        mock_get.return_value = exercise
        mock_update.return_value = exercise
        validated_data = {"name": "Updated"}

        # Act
        result = update_exercise_service(
            exercise_id=exercise.id, validated_data=validated_data, user=self.user
        )

        # Assert
        self.assertIsNotNone(result)
        mock_get.assert_called_once_with(exercise_id=exercise.id)
        mock_update.assert_called_once()

    @patch("apps.exercises.services.get_exercise_by_id_repository")
    def test_update_exercise_service_non_existing(self, mock_repository):
        """Test: Actualizar ejercicio inexistente."""
        # Arrange
        mock_repository.return_value = None
        validated_data = {"name": "Updated"}

        # Act & Assert
        with self.assertRaises(NotFound):
            update_exercise_service(exercise_id=999, validated_data=validated_data, user=self.user)

        mock_repository.assert_called_once_with(exercise_id=999)

    @patch("apps.exercises.services.get_exercise_by_id_repository")
    def test_update_exercise_service_permission_denied(self, mock_repository):
        """Test: Actualizar ejercicio sin permisos."""
        # Arrange
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        exercise = Exercise.objects.create(name="Original", created_by=other_user)
        mock_repository.return_value = exercise
        validated_data = {"name": "Updated"}

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            update_exercise_service(
                exercise_id=exercise.id, validated_data=validated_data, user=self.user
            )

    @patch("apps.exercises.services.get_exercise_by_id_repository")
    @patch("apps.exercises.services.delete_exercise_repository")
    def test_delete_exercise_service_success(self, mock_delete, mock_get):
        """Test: Eliminar ejercicio exitosamente."""
        # Arrange
        exercise = Exercise.objects.create(name="To Delete", created_by=self.user)
        exercise.is_active = False
        mock_get.return_value = exercise
        mock_delete.return_value = exercise

        # Act
        result = delete_exercise_service(exercise_id=exercise.id, user=self.user)

        # Assert
        self.assertIsNotNone(result)
        mock_get.assert_called_once_with(exercise_id=exercise.id)
        mock_delete.assert_called_once_with(exercise=exercise)

    @patch("apps.exercises.services.get_exercise_by_id_repository")
    def test_delete_exercise_service_non_existing(self, mock_repository):
        """Test: Eliminar ejercicio inexistente."""
        # Arrange
        mock_repository.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            delete_exercise_service(exercise_id=999, user=self.user)

        mock_repository.assert_called_once_with(exercise_id=999)

    @patch("apps.exercises.services.get_exercise_by_id_repository")
    def test_delete_exercise_service_permission_denied(self, mock_repository):
        """Test: Eliminar ejercicio sin permisos."""
        # Arrange
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        exercise = Exercise.objects.create(name="To Delete", created_by=other_user)
        mock_repository.return_value = exercise

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            delete_exercise_service(exercise_id=exercise.id, user=self.user)


# ============================================================================
# Tests Unitarios - Serializers
# ============================================================================


class ExerciseSerializerTestCase(TestCase):
    """Tests unitarios para los serializadores de Exercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.movement_type = MovementTypeFactory(name="push", display_name="Push")
        self.muscle_group = MuscleGroupFactory(
            name="chest", display_name="Chest", parent=None
        )  # Grupo principal
        self.equipment = EquipmentFactory(name="barbell", display_name="Barbell")
        self.shoulders = MuscleGroupFactory(
            name="shoulders", display_name="Shoulders", parent=None
        )  # Grupo principal
        self.arms = MuscleGroupFactory(
            name="arms", display_name="Arms", parent=None
        )  # Grupo principal

        self.exercise = Exercise.objects.create(
            name="Test Exercise",
            description="Test description",
            movement_type=self.movement_type,
            primary_muscle_group=self.muscle_group,
            secondary_muscle_groups=["shoulders", "arms"],
            equipment=self.equipment,
            difficulty="intermediate",
            instructions="Test instructions",
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            is_active=True,
            created_by=self.user,
        )

    def test_exercise_serializer_serialization(self):
        """Test: Serialización de ejercicio."""
        # Arrange
        serializer = ExerciseSerializer(self.exercise)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.exercise.id)
        self.assertEqual(data["name"], "Test Exercise")
        self.assertEqual(data["description"], "Test description")
        self.assertEqual(data["movementType"], "push")
        self.assertEqual(data["primaryMuscleGroup"], "chest")
        self.assertEqual(data["secondaryMuscleGroups"], ["shoulders", "arms"])
        self.assertEqual(data["equipment"], "barbell")
        self.assertEqual(data["difficulty"], "intermediate")
        self.assertEqual(data["instructions"], "Test instructions")
        self.assertEqual(data["imageUrl"], "https://example.com/image.jpg")
        self.assertEqual(data["videoUrl"], "https://example.com/video.mp4")
        self.assertTrue(data["isActive"])
        self.assertEqual(data["createdBy"], "testuser")
        self.assertIn("createdAt", data)
        self.assertIn("updatedAt", data)

    def test_exercise_serializer_created_by_none(self):
        """Test: Serialización con created_by None."""
        # Arrange
        exercise = Exercise.objects.create(name="No Creator")
        serializer = ExerciseSerializer(exercise)

        # Act
        data = serializer.data

        # Assert
        self.assertIsNone(data["createdBy"])

    def test_exercise_create_serializer_valid_data(self):
        """Test: Serializador de creación con datos válidos."""
        # Arrange
        data = {
            "name": "New Exercise",
            "description": "New description",
            "movementType": "pull",
            "primaryMuscleGroup": "back",
            "secondaryMuscleGroups": ["arms"],
            "equipment": "dumbbell",
            "difficulty": "beginner",
            "instructions": "New instructions",
            "imageUrl": "https://example.com/new.jpg",
            "videoUrl": "https://example.com/new.mp4",
            "isActive": True,
        }

        # Act
        serializer = ExerciseCreateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "New Exercise")

    def test_exercise_create_serializer_name_required(self):
        """Test: Serializador de creación requiere nombre."""
        # Arrange
        data = {"description": "No name"}

        # Act
        serializer = ExerciseCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_exercise_create_serializer_name_empty(self):
        """Test: Serializador de creación con nombre vacío."""
        # Arrange
        data = {"name": "   "}

        # Act
        serializer = ExerciseCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_exercise_create_serializer_invalid_secondary_muscle_groups(self):
        """Test: Serializador de creación con secondaryMuscleGroups inválido."""
        # Arrange
        data = {"name": "Test", "secondaryMuscleGroups": ["invalid_group"]}

        # Act
        serializer = ExerciseCreateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("secondaryMuscleGroups", serializer.errors)

    def test_exercise_update_serializer_valid_data(self):
        """Test: Serializador de actualización con datos válidos."""
        # Arrange
        data = {"name": "Updated Exercise", "difficulty": "advanced"}

        # Act
        serializer = ExerciseUpdateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Updated Exercise")
        self.assertEqual(serializer.validated_data["difficulty"], "advanced")

    def test_exercise_update_serializer_name_empty(self):
        """Test: Serializador de actualización con nombre vacío."""
        # Arrange
        data = {"name": "   "}

        # Act
        serializer = ExerciseUpdateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_exercise_update_serializer_partial_update(self):
        """Test: Serializador de actualización permite actualización parcial."""
        # Arrange
        data = {"difficulty": "advanced"}

        # Act
        serializer = ExerciseUpdateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["difficulty"], "advanced")


# ============================================================================
# Tests Unitarios - Forms
# ============================================================================


class ExerciseFormTestCase(TestCase):
    """Tests unitarios para los formularios de Exercise."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Configura datos de prueba que no cambian."""
        cls.main_muscle_group = MuscleGroupFactory(name="chest", display_name="Chest", parent=None)
        cls.sub_muscle_group1 = MuscleGroupFactory(
            name="upper_chest", display_name="Upper Chest", parent=cls.main_muscle_group
        )
        cls.sub_muscle_group2 = MuscleGroupFactory(
            name="lower_chest", display_name="Lower Chest", parent=cls.main_muscle_group
        )
        cls.other_main_group = MuscleGroupFactory(name="back", display_name="Back", parent=None)
        cls.other_sub_group = MuscleGroupFactory(
            name="lats", display_name="Lats", parent=cls.other_main_group
        )

    def test_exercise_create_form_valid_data(self) -> None:
        """Test: Formulario de creación con datos válidos."""
        # Arrange
        form_data = {
            "name": "Test Exercise",
            "description": "Test description",
            "movement_type": "push",
            "primary_muscle_group": "chest",  # Obligatorio ahora
            "equipment": "barbell",
            "difficulty": "intermediate",
        }

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Test Exercise")
        self.assertEqual(form.cleaned_data["primary_muscle_group"].name, "chest")

    def test_exercise_create_form_primary_muscle_group_required(self) -> None:
        """Test: Formulario de creación requiere grupo muscular principal."""
        # Arrange
        form_data = {"name": "Test Exercise"}  # Sin primary_muscle_group

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn("primary_muscle_group", form.errors)

    def test_exercise_create_form_primary_muscle_group_only_main_groups(self) -> None:
        """Test: Formulario solo muestra grupos principales en primary_muscle_group."""
        # Arrange
        form = ExerciseCreateForm()

        # Act
        queryset = form.fields["primary_muscle_group"].queryset

        # Assert
        # Solo debe incluir grupos principales (sin parent)
        for group in queryset:
            self.assertIsNone(group.parent, f"{group.name} no debería tener parent")

    def test_exercise_create_form_secondary_muscle_groups_optional(self) -> None:
        """Test: Formulario permite crear ejercicio sin grupos secundarios."""
        # Arrange
        form_data = {
            "name": "Test Exercise",
            "primary_muscle_group": "chest",
        }

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get("secondary_muscle_groups"), [])

    def test_exercise_create_form_secondary_muscle_groups_multiple(self) -> None:
        """Test: Formulario permite seleccionar múltiples grupos secundarios."""
        # Arrange
        form_data = {
            "name": "Test Exercise",
            "primary_muscle_group": "chest",
            "secondary_muscle_groups": [self.sub_muscle_group1.id, self.sub_muscle_group2.id],
        }

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())
        secondary_groups = form.cleaned_data.get("secondary_muscle_groups")
        self.assertIsNotNone(secondary_groups)
        self.assertEqual(len(secondary_groups), 2)
        # Ahora devuelve objetos MuscleGroup
        secondary_names = [sg.name for sg in secondary_groups]
        self.assertIn("upper_chest", secondary_names)
        self.assertIn("lower_chest", secondary_names)

    def test_exercise_create_form_secondary_muscle_groups_validation(self) -> None:
        """Test: Formulario valida que grupos secundarios sean hijos del principal."""
        # Arrange
        form_data = {
            "name": "Test Exercise",
            "primary_muscle_group": "chest",
            "secondary_muscle_groups": [
                self.other_sub_group.id
            ],  # Grupo secundario de otro grupo principal
        }

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn("secondary_muscle_groups", form.errors)

    def test_exercise_create_form_secondary_without_primary(self) -> None:
        """Test: Formulario no permite grupos secundarios sin grupo principal."""
        # Arrange
        form_data = {
            "name": "Test Exercise",
            "secondary_muscle_groups": [self.sub_muscle_group1.id],
        }

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        # Debe tener error en clean() (non_field_errors) o en secondary_muscle_groups
        self.assertTrue(
            "secondary_muscle_groups" in form.errors
            or "__all__" in form.errors
            or "primary_muscle_group" in form.errors
        )

    def test_exercise_create_form_name_required(self):
        """Test: Formulario de creación requiere nombre."""
        # Arrange
        form_data = {"description": "No name"}

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_exercise_create_form_name_empty(self):
        """Test: Formulario de creación con nombre vacío."""
        # Arrange
        form_data = {"name": "   "}

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_exercise_update_form_valid_data(self):
        """Test: Formulario de actualización con datos válidos."""
        # Arrange
        form_data = {"name": "Updated Exercise"}

        # Act
        form = ExerciseUpdateForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Updated Exercise")

    def test_exercise_update_form_name_not_required(self):
        """Test: Formulario de actualización no requiere nombre."""
        # Arrange
        form_data = {"difficulty": "advanced"}

        # Act
        form = ExerciseUpdateForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())

    def test_exercise_form_clean_movement_type_empty_string(self):
        """Test: Formulario limpia movement_type vacío."""
        # Arrange
        form_data = {"name": "Test", "movement_type": "", "primary_muscle_group": "chest"}

        # Act
        form = ExerciseCreateForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data["movement_type"])


# ============================================================================
# Tests de Integración - API Views
# ============================================================================


class ExerciseAPITestCase(TestCase):
    """Tests de integración para las vistas API de Exercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.muscle_group = MuscleGroupFactory(
            name="chest", display_name="Chest", parent=None
        )  # Grupo principal
        self.equipment = EquipmentFactory(name="barbell", display_name="Barbell")

        self.exercise = Exercise.objects.create(
            name="Test Exercise",
            primary_muscle_group=self.muscle_group,
            equipment=self.equipment,
            difficulty="intermediate",
            created_by=self.user,
        )

    def test_exercise_list_api_get_success(self):
        """Test: GET /api/exercises/ exitoso."""
        # Arrange & Act
        response = self.client.get("/api/exercises/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["name"], "Test Exercise")

    def test_exercise_list_api_get_with_filters(self):
        """Test: GET /api/exercises/ con filtros."""
        # Arrange
        back = MuscleGroupFactory(name="back", display_name="Back")
        dumbbell = EquipmentFactory(name="dumbbell", display_name="Dumbbell")
        Exercise.objects.create(
            name="Other Exercise",
            primary_muscle_group=back,
            equipment=dumbbell,
        )

        # Act
        response = self.client.get("/api/exercises/?primaryMuscleGroup=chest")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["primaryMuscleGroup"], "chest")

    def test_exercise_list_api_get_with_search(self):
        """Test: GET /api/exercises/ con búsqueda."""
        # Arrange
        Exercise.objects.create(name="Different Exercise")

        # Act
        response = self.client.get("/api/exercises/?search=Test")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["name"], "Test Exercise")

    def test_exercise_list_api_post_success(self):
        """Test: POST /api/exercises/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "New Exercise",
            "primaryMuscleGroup": "chest",
            "equipment": "barbell",
            "difficulty": "beginner",
        }

        # Act
        response = self.client.post("/api/exercises/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["name"], "New Exercise")
        self.assertIn("message", response.data)

    def test_exercise_list_api_post_unauthenticated(self):
        """Test: POST /api/exercises/ sin autenticación."""
        # Arrange
        data = {"name": "New Exercise"}

        # Act
        response = self.client.post("/api/exercises/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_exercise_list_api_post_invalid_data(self):
        """Test: POST /api/exercises/ con datos inválidos."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {"name": "   "}  # Nombre vacío

        # Act
        response = self.client.post("/api/exercises/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_exercise_detail_api_get_success(self):
        """Test: GET /api/exercises/{id}/ exitoso."""
        # Arrange & Act
        response = self.client.get(f"/api/exercises/{self.exercise.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["name"], "Test Exercise")

    def test_exercise_detail_api_get_not_found(self):
        """Test: GET /api/exercises/{id}/ no encontrado."""
        # Arrange & Act
        response = self.client.get("/api/exercises/99999/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_exercise_detail_api_put_success(self):
        """Test: PUT /api/exercises/{id}/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {"name": "Updated Exercise"}

        # Act
        response = self.client.put(f"/api/exercises/{self.exercise.id}/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Updated Exercise")
        self.assertIn("message", response.data)

    def test_exercise_detail_api_put_unauthenticated(self):
        """Test: PUT /api/exercises/{id}/ sin autenticación."""
        # Arrange
        data = {"name": "Updated Exercise"}

        # Act
        response = self.client.put(f"/api/exercises/{self.exercise.id}/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_exercise_detail_api_put_permission_denied(self):
        """Test: PUT /api/exercises/{id}/ sin permisos."""
        # Arrange
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=other_user)
        data = {"name": "Updated Exercise"}

        # Act
        response = self.client.put(f"/api/exercises/{self.exercise.id}/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)

    def test_exercise_detail_api_delete_success(self):
        """Test: DELETE /api/exercises/{id}/ exitoso."""
        # Arrange
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.delete(f"/api/exercises/{self.exercise.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verificar soft delete
        self.exercise.refresh_from_db()
        self.assertFalse(self.exercise.is_active)

    def test_exercise_detail_api_delete_unauthenticated(self):
        """Test: DELETE /api/exercises/{id}/ sin autenticación."""
        # Arrange & Act
        response = self.client.delete(f"/api/exercises/{self.exercise.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_exercise_detail_api_delete_permission_denied(self):
        """Test: DELETE /api/exercises/{id}/ sin permisos."""
        # Arrange
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=other_user)

        # Act
        response = self.client.delete(f"/api/exercises/{self.exercise.id}/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)


# ============================================================================
# Tests de Integración - Web Views
# ============================================================================


class ExerciseWebViewTestCase(TestCase):
    """Tests de integración para las vistas web de Exercise."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.muscle_group = MuscleGroupFactory(name="chest", display_name="Chest")
        self.equipment = EquipmentFactory(name="barbell", display_name="Barbell")

        self.exercise = Exercise.objects.create(
            name="Test Exercise",
            primary_muscle_group=self.muscle_group,
            equipment=self.equipment,
            difficulty="intermediate",
            created_by=self.user,
        )

    def test_exercise_list_view_get(self):
        """Test: Vista de lista de ejercicios."""
        # Arrange & Act
        response = self.client.get("/exercises/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("exercises", response.context)

    def test_exercise_list_view_get_with_filters(self):
        """Test: Vista de lista con filtros."""
        # Arrange & Act
        response = self.client.get("/exercises/?primaryMuscleGroup=chest")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("exercises", response.context)

    def test_exercise_detail_view_get(self):
        """Test: Vista de detalle de ejercicio."""
        # Arrange & Act
        response = self.client.get(f"/exercises/{self.exercise.id}/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("exercise", response.context)
        self.assertEqual(response.context["exercise"]["name"], "Test Exercise")

    def test_exercise_detail_view_get_not_found(self):
        """Test: Vista de detalle con ejercicio inexistente."""
        # Arrange & Act
        response = self.client.get("/exercises/99999/")

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_exercise_create_view_get_authenticated(self):
        """Test: Vista de creación GET autenticado."""
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get("/exercises/create/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_exercise_create_view_get_unauthenticated(self):
        """Test: Vista de creación GET sin autenticación."""
        # Arrange & Act
        response = self.client.get("/exercises/create/")

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_exercise_create_view_post_success(self) -> None:
        """Test: Vista de creación POST exitoso."""
        # Arrange
        self.client.force_login(self.user)
        # Asegurar que chest es un grupo principal
        main_group = MuscleGroup.objects.filter(name="chest", parent=None).first()
        if not main_group:
            main_group = MuscleGroupFactory(name="chest", display_name="Chest", parent=None)
        data = {
            "name": "New Exercise",
            "primary_muscle_group": "chest",
            "equipment": "barbell",
            "difficulty": "beginner",
        }

        # Act
        response = self.client.post("/exercises/create/", data)

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Exercise.objects.filter(name="New Exercise").exists())

    def test_exercise_create_view_get_with_muscle_groups_data(self) -> None:
        """Test: Vista de creación GET incluye datos de grupos musculares en contexto."""
        # Arrange
        self.client.force_login(self.user)
        main_group = MuscleGroupFactory(name="chest", display_name="Chest", parent=None)
        MuscleGroupFactory(name="upper_chest", display_name="Upper Chest", parent=main_group)

        # Act
        response = self.client.get("/exercises/create/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("muscle_groups_data", response.context)
        muscle_groups_data = response.context["muscle_groups_data"]
        # Ahora es un diccionario indexado por name
        self.assertIsInstance(muscle_groups_data, dict)
        self.assertIn(main_group.name, muscle_groups_data)
        self.assertEqual(len(muscle_groups_data[main_group.name]["subgroups"]), 1)
        self.assertEqual(muscle_groups_data[main_group.name]["subgroups"][0]["name"], "upper_chest")

    def test_exercise_create_view_post_with_secondary_groups(self) -> None:
        """Test: Vista de creación POST con grupos secundarios."""
        # Arrange
        self.client.force_login(self.user)
        main_group = MuscleGroupFactory(name="chest", display_name="Chest", parent=None)
        sub_group1 = MuscleGroupFactory(
            name="upper_chest", display_name="Upper Chest", parent=main_group
        )
        sub_group2 = MuscleGroupFactory(
            name="lower_chest", display_name="Lower Chest", parent=main_group
        )
        data = {
            "name": "New Exercise",
            "primary_muscle_group": "chest",
            "secondary_muscle_groups": [sub_group1.id, sub_group2.id],
            "equipment": "barbell",
            "difficulty": "beginner",
        }

        # Act
        response = self.client.post("/exercises/create/", data)

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        exercise = Exercise.objects.get(name="New Exercise")
        self.assertEqual(exercise.primary_muscle_group.name, "chest")
        self.assertIn("upper_chest", exercise.secondary_muscle_groups)
        self.assertIn("lower_chest", exercise.secondary_muscle_groups)

    def test_exercise_update_view_post_with_secondary_groups(self) -> None:
        """Test: Vista de actualización POST con grupos secundarios."""
        # Arrange
        self.client.force_login(self.user)
        main_group = MuscleGroupFactory(name="chest", display_name="Chest", parent=None)
        sub_group = MuscleGroupFactory(
            name="upper_chest", display_name="Upper Chest", parent=main_group
        )
        self.exercise.primary_muscle_group = main_group
        self.exercise.save()
        data = {
            "name": "Updated Exercise",
            "primary_muscle_group": "chest",
            "secondary_muscle_groups": [sub_group.id],
        }

        # Act
        response = self.client.post(f"/exercises/{self.exercise.id}/update/", data)

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        self.exercise.refresh_from_db()
        self.assertIn("upper_chest", self.exercise.secondary_muscle_groups)

    def test_exercise_update_view_get_authenticated_owner(self):
        """Test: Vista de actualización GET como propietario."""
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get(f"/exercises/{self.exercise.id}/update/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_exercise_update_view_get_permission_denied(self):
        """Test: Vista de actualización GET sin permisos."""
        # Arrange
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_login(other_user)

        # Act
        response = self.client.get(f"/exercises/{self.exercise.id}/update/")

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_exercise_delete_view_post_success(self):
        """Test: Vista de eliminación POST exitoso."""
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.post(f"/exercises/{self.exercise.id}/delete/")

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        self.exercise.refresh_from_db()
        self.assertFalse(self.exercise.is_active)

    def test_exercise_delete_view_post_permission_denied(self):
        """Test: Vista de eliminación POST sin permisos."""
        # Arrange
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_login(other_user)

        # Act
        response = self.client.post(f"/exercises/{self.exercise.id}/delete/")

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        self.exercise.refresh_from_db()
        self.assertTrue(self.exercise.is_active)  # No se eliminó


# ============================================================================
# Tests Unitarios - MuscleGroup (Jerarquía)
# ============================================================================


class MuscleGroupHierarchyTestCase(TestCase):
    """Tests unitarios para la funcionalidad jerárquica de MuscleGroup."""

    def setUp(self):
        """Arrange: Configura datos de prueba."""
        # Crear grupos musculares principales
        self.legs = MuscleGroupFactory(name="legs", display_name="Legs", parent=None)
        self.arms = MuscleGroupFactory(name="arms", display_name="Arms", parent=None)
        # Crear subgrupos
        self.quadriceps = MuscleGroupFactory(
            name="quadriceps", display_name="Quadriceps", parent=self.legs
        )
        self.hamstrings = MuscleGroupFactory(
            name="hamstrings", display_name="Hamstrings", parent=self.legs
        )
        self.biceps = MuscleGroupFactory(name="biceps", display_name="Biceps", parent=self.arms)

    def test_muscle_group_without_parent(self):
        """Test: Grupo muscular sin padre muestra solo su nombre."""
        # Act
        str_repr = str(self.legs)

        # Assert
        self.assertEqual(str_repr, "Legs")
        self.assertIsNone(self.legs.parent)

    def test_muscle_group_with_parent(self):
        """Test: Grupo muscular con padre muestra jerarchía."""
        # Act
        str_repr = str(self.quadriceps)

        # Assert
        self.assertEqual(str_repr, "Legs > Quadriceps")
        self.assertEqual(self.quadriceps.parent, self.legs)

    def test_muscle_group_subgroups_relationship(self):
        """Test: Acceso a subgrupos desde el padre."""
        # Act
        subgroups = list(self.legs.subgroups.all())

        # Assert
        self.assertEqual(len(subgroups), 2)
        self.assertIn(self.quadriceps, subgroups)
        self.assertIn(self.hamstrings, subgroups)
        self.assertNotIn(self.biceps, subgroups)

    def test_muscle_group_cascade_delete(self):
        """Test: Eliminar grupo padre elimina subgrupos (CASCADE)."""
        # Arrange
        quadriceps_id = self.quadriceps.id
        hamstrings_id = self.hamstrings.id

        # Act
        self.legs.delete()

        # Assert
        self.assertFalse(MuscleGroup.objects.filter(id=quadriceps_id).exists())
        self.assertFalse(MuscleGroup.objects.filter(id=hamstrings_id).exists())
        # El grupo de brazos y bíceps deben seguir existiendo
        self.assertTrue(MuscleGroup.objects.filter(id=self.arms.id).exists())
        self.assertTrue(MuscleGroup.objects.filter(id=self.biceps.id).exists())

    def test_muscle_group_self_reference_prevention(self):
        """Test: Un grupo no puede ser su propio padre."""
        # Arrange
        from django.core.exceptions import ValidationError as DjangoValidationError

        muscle_group = MuscleGroupFactory(name="test", display_name="Test")

        # Act & Assert
        with self.assertRaises(DjangoValidationError):
            muscle_group.parent = muscle_group
            muscle_group.full_clean()

    def test_muscle_group_circular_reference_prevention(self):
        """Test: Prevenir referencias circulares (padre no puede ser hijo de su hijo)."""
        # Arrange
        from django.core.exceptions import ValidationError as DjangoValidationError

        parent = MuscleGroupFactory(name="parent", display_name="Parent")
        child = MuscleGroupFactory(name="child", display_name="Child", parent=parent)

        # Act & Assert
        # Intentar hacer que el padre sea hijo del hijo debería fallar
        with self.assertRaises(DjangoValidationError):
            parent.parent = child
            parent.full_clean()

    def test_muscle_group_serializer_without_parent(self):
        """Test: Serializador de grupo sin padre."""
        # Arrange
        from apps.exercises.serializers import MuscleGroupSerializer

        serializer = MuscleGroupSerializer(self.legs)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.legs.id)
        self.assertEqual(data["name"], "legs")
        self.assertEqual(data["displayName"], "Legs")
        self.assertIsNone(data["parent"])
        self.assertIsNone(data["parentId"])
        self.assertIsInstance(data["subgroups"], list)
        self.assertEqual(len(data["subgroups"]), 2)

    def test_muscle_group_serializer_with_parent(self):
        """Test: Serializador de grupo con padre."""
        # Arrange
        from apps.exercises.serializers import MuscleGroupSerializer

        serializer = MuscleGroupSerializer(self.quadriceps)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(data["id"], self.quadriceps.id)
        self.assertEqual(data["name"], "quadriceps")
        self.assertEqual(data["displayName"], "Quadriceps")
        self.assertIsNotNone(data["parent"])
        self.assertEqual(data["parent"]["id"], self.legs.id)
        self.assertEqual(data["parent"]["name"], "legs")
        self.assertEqual(data["parent"]["displayName"], "Legs")
        self.assertEqual(data["parentId"], self.legs.id)
        self.assertIsInstance(data["subgroups"], list)

    def test_muscle_group_serializer_subgroups(self):
        """Test: Serializador incluye subgrupos."""
        # Arrange
        from apps.exercises.serializers import MuscleGroupSerializer

        serializer = MuscleGroupSerializer(self.legs)

        # Act
        data = serializer.data

        # Assert
        self.assertEqual(len(data["subgroups"]), 2)
        subgroup_names = [sg["name"] for sg in data["subgroups"]]
        self.assertIn("quadriceps", subgroup_names)
        self.assertIn("hamstrings", subgroup_names)
