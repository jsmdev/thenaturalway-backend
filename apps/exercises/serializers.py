from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import serializers

from apps.exercises.models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    """
    Serializador para representar un ejercicio completo.

    Este serializador se usa para representar ejercicios en respuestas de la API.
    Incluye todos los campos del modelo con nombres en camelCase para la API.

    **Campos:**
    - `id` (int, read-only): ID único del ejercicio
    - `name` (str): Nombre del ejercicio
    - `description` (str, opcional): Descripción del ejercicio
    - `movementType` (str, opcional): Tipo de movimiento (push, pull, squat, hinge, carry, other)
    - `primaryMuscleGroup` (str, opcional): Grupo muscular principal
    - `secondaryMuscleGroups` (array[str], opcional): Grupos musculares secundarios
    - `equipment` (str, opcional): Equipamiento necesario
    - `difficulty` (str, opcional): Nivel de dificultad (beginner, intermediate, advanced)
    - `instructions` (str, opcional): Instrucciones de ejecución
    - `imageUrl` (str, opcional): URL de imagen del ejercicio
    - `videoUrl` (str, opcional): URL de video del ejercicio
    - `isActive` (bool): Estado activo del ejercicio
    - `createdBy` (str, opcional): Username del creador (calculado)
    - `createdAt` (datetime, read-only): Fecha de creación
    - `updatedAt` (datetime, read-only): Fecha de última actualización
    """

    # Campos calculados
    createdBy = serializers.SerializerMethodField()
    movementType = serializers.CharField(source="movement_type", required=False, allow_null=True)
    primaryMuscleGroup = serializers.CharField(
        source="primary_muscle_group", required=False, allow_null=True
    )
    secondaryMuscleGroups = serializers.JSONField(
        source="secondary_muscle_groups", required=False, allow_null=True
    )
    equipment = serializers.CharField(required=False, allow_null=True)
    difficulty = serializers.CharField(required=False, allow_null=True)
    instructions = serializers.CharField(required=False, allow_null=True)
    imageUrl = serializers.URLField(source="image_url", required=False, allow_null=True)
    videoUrl = serializers.URLField(source="video_url", required=False, allow_null=True)
    isActive = serializers.BooleanField(source="is_active", required=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Exercise
        fields: ClassVar[list[str]] = [
            "id",
            "name",
            "description",
            "movementType",
            "primaryMuscleGroup",
            "secondaryMuscleGroups",
            "equipment",
            "difficulty",
            "instructions",
            "imageUrl",
            "videoUrl",
            "isActive",
            "createdBy",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields: ClassVar[list[str]] = ["id", "createdAt", "updatedAt"]

    def get_createdBy(self, obj: Exercise) -> Any:
        """Retorna el username o id del creador."""
        if obj.created_by:
            return obj.created_by.username
        return None


class ExerciseCreateSerializer(serializers.Serializer):
    """
    Serializador para crear un nuevo ejercicio.

    Este serializador valida los datos de entrada para crear un nuevo ejercicio.
    El campo `name` es requerido, todos los demás son opcionales.

    **Campos requeridos:**
    - `name` (str, max_length=255): Nombre del ejercicio

    **Campos opcionales:**
    - `description` (str): Descripción del ejercicio
    - `movementType` (str): Tipo de movimiento
    - `primaryMuscleGroup` (str): Grupo muscular principal
    - `secondaryMuscleGroups` (array[str]): Grupos musculares secundarios
    - `equipment` (str): Equipamiento necesario
    - `difficulty` (str): Nivel de dificultad
    - `instructions` (str): Instrucciones de ejecución
    - `imageUrl` (str): URL de imagen (debe ser una URL válida)
    - `videoUrl` (str): URL de video (debe ser una URL válida)
    - `isActive` (bool, default=True): Estado activo

    **Validaciones:**
    - `name`: No puede estar vacío ni contener solo espacios
    - `secondaryMuscleGroups`: Debe ser un array de strings válidos
    - Todos los campos de tipo enum validan contra las opciones del modelo

    **Ejemplo de uso:**
    ```python
    serializer = ExerciseCreateSerializer(data={
        "name": "Bench Press",
        "primaryMuscleGroup": "chest",
        "equipment": "barbell"
    })
    if serializer.is_valid():
        exercise = create_exercise_service(serializer.validated_data, user)
    ```
    """

    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    movementType = serializers.ChoiceField(
        choices=Exercise.MOVEMENT_TYPE_CHOICES, required=False, allow_null=True
    )
    primaryMuscleGroup = serializers.ChoiceField(
        choices=Exercise.PRIMARY_MUSCLE_GROUP_CHOICES, required=False, allow_null=True
    )
    secondaryMuscleGroups = serializers.ListField(
        child=serializers.ChoiceField(choices=Exercise.PRIMARY_MUSCLE_GROUP_CHOICES),
        required=False,
        allow_empty=True,
    )
    equipment = serializers.ChoiceField(
        choices=Exercise.EQUIPMENT_CHOICES, required=False, allow_null=True
    )
    difficulty = serializers.ChoiceField(
        choices=Exercise.DIFFICULTY_CHOICES, required=False, allow_null=True
    )
    instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imageUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    videoUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    isActive = serializers.BooleanField(required=False, default=True)

    def validate_name(self, value: str) -> str:
        """Valida que el nombre no esté vacío."""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value.strip()

    def validate_secondaryMuscleGroups(self, value: list) -> list:
        """Valida que secondaryMuscleGroups sea un array de strings válidos."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Debe ser un array")
        valid_groups = [choice[0] for choice in Exercise.PRIMARY_MUSCLE_GROUP_CHOICES]
        for group in value:
            if not isinstance(group, str):
                raise serializers.ValidationError("Todos los elementos deben ser strings")
            if group not in valid_groups:
                raise serializers.ValidationError(
                    f"Cada elemento debe ser uno de: {', '.join(valid_groups)}"
                )
        return value


class ExerciseUpdateSerializer(serializers.Serializer):
    """
    Serializador para actualizar un ejercicio existente.

    Este serializador valida los datos de entrada para actualizar un ejercicio existente.
    Todos los campos son opcionales (solo se actualizan los proporcionados).

    **Campos opcionales:**
    - `name` (str, max_length=255): Nombre del ejercicio
    - `description` (str): Descripción del ejercicio
    - `movementType` (str): Tipo de movimiento
    - `primaryMuscleGroup` (str): Grupo muscular principal
    - `secondaryMuscleGroups` (array[str]): Grupos musculares secundarios
    - `equipment` (str): Equipamiento necesario
    - `difficulty` (str): Nivel de dificultad
    - `instructions` (str): Instrucciones de ejecución
    - `imageUrl` (str): URL de imagen (debe ser una URL válida)
    - `videoUrl` (str): URL de video (debe ser una URL válida)
    - `isActive` (bool): Estado activo

    **Validaciones:**
    - `name`: Si se proporciona, no puede estar vacío ni contener solo espacios
    - `secondaryMuscleGroups`: Debe ser un array de strings válidos
    - Todos los campos de tipo enum validan contra las opciones del modelo

    **Ejemplo de uso:**
    ```python
    serializer = ExerciseUpdateSerializer(data={
        "name": "Bench Press Updated",
        "difficulty": "advanced"
    })
    if serializer.is_valid():
        exercise = update_exercise_service(exercise_id, serializer.validated_data, user)
    ```
    """

    name = serializers.CharField(required=False, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    movementType = serializers.ChoiceField(
        choices=Exercise.MOVEMENT_TYPE_CHOICES, required=False, allow_null=True
    )
    primaryMuscleGroup = serializers.ChoiceField(
        choices=Exercise.PRIMARY_MUSCLE_GROUP_CHOICES, required=False, allow_null=True
    )
    secondaryMuscleGroups = serializers.ListField(
        child=serializers.ChoiceField(choices=Exercise.PRIMARY_MUSCLE_GROUP_CHOICES),
        required=False,
        allow_empty=True,
    )
    equipment = serializers.ChoiceField(
        choices=Exercise.EQUIPMENT_CHOICES, required=False, allow_null=True
    )
    difficulty = serializers.ChoiceField(
        choices=Exercise.DIFFICULTY_CHOICES, required=False, allow_null=True
    )
    instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imageUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    videoUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    isActive = serializers.BooleanField(required=False)

    def validate_name(self, value: str) -> str:
        """Valida que el nombre no esté vacío si se proporciona."""
        if value and not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value.strip() if value else value

    def validate_secondaryMuscleGroups(self, value: list) -> list:
        """Valida que secondaryMuscleGroups sea un array de strings válidos."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Debe ser un array")
        valid_groups = [choice[0] for choice in Exercise.PRIMARY_MUSCLE_GROUP_CHOICES]
        for group in value:
            if not isinstance(group, str):
                raise serializers.ValidationError("Todos los elementos deben ser strings")
            if group not in valid_groups:
                raise serializers.ValidationError(
                    f"Cada elemento debe ser uno de: {', '.join(valid_groups)}"
                )
        return value
