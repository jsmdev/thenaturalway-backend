from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import serializers

from apps.exercises.models import Difficulty, Equipment, Exercise, MovementType, MuscleGroup


class MuscleGroupSerializer(serializers.ModelSerializer):
    """
    Serializador para representar grupos musculares con soporte jerárquico.

    Este serializador incluye información sobre el grupo padre y los subgrupos.
    """

    displayName = serializers.CharField(source="display_name", read_only=True)
    parent = serializers.SerializerMethodField()
    parentId = serializers.IntegerField(source="parent.id", read_only=True, allow_null=True)
    subgroups = serializers.SerializerMethodField()
    isActive = serializers.BooleanField(source="is_active", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = MuscleGroup
        fields: ClassVar[list[str]] = [
            "id",
            "name",
            "displayName",
            "description",
            "parent",
            "parentId",
            "subgroups",
            "isActive",
            "order",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields: ClassVar[list[str]] = ["id", "createdAt", "updatedAt"]

    def get_parent(self, obj: MuscleGroup) -> dict[str, Any] | None:
        """Retorna información del grupo padre si existe."""
        if obj.parent:
            return {
                "id": obj.parent.id,
                "name": obj.parent.name,
                "displayName": obj.parent.display_name,
            }
        return None

    def get_subgroups(self, obj: MuscleGroup) -> list[dict[str, Any]]:
        """Retorna lista de subgrupos."""
        subgroups = obj.subgroups.filter(is_active=True).order_by("order", "name")
        return [
            {
                "id": subgroup.id,
                "name": subgroup.name,
                "displayName": subgroup.display_name,
            }
            for subgroup in subgroups
        ]


class DifficultySerializer(serializers.ModelSerializer):
    """
    Serializador para representar niveles de dificultad.
    """

    displayName = serializers.CharField(source="display_name", read_only=True)
    isActive = serializers.BooleanField(source="is_active", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Difficulty
        fields: ClassVar[list[str]] = [
            "id",
            "name",
            "displayName",
            "description",
            "isActive",
            "order",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields: ClassVar[list[str]] = ["id", "createdAt", "updatedAt"]


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
    - `difficulty` (dict, opcional): Nivel de dificultad con name y displayName
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
    movementType = serializers.SerializerMethodField()
    primaryMuscleGroup = serializers.SerializerMethodField()
    secondaryMuscleGroups = serializers.JSONField(
        source="secondary_muscle_groups", required=False, allow_null=True
    )
    equipment = serializers.SerializerMethodField()
    difficulty = serializers.SerializerMethodField()
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

    def get_movementType(self, obj: Exercise) -> dict[str, Any] | None:
        """Retorna el tipo de movimiento con name y displayName."""
        if obj.movement_type:
            return {
                "name": obj.movement_type.name,
                "displayName": obj.movement_type.display_name,
            }
        return None

    def get_primaryMuscleGroup(self, obj: Exercise) -> dict[str, Any] | None:
        """Retorna el grupo muscular principal con name y displayName."""
        if obj.primary_muscle_group:
            return {
                "name": obj.primary_muscle_group.name,
                "displayName": obj.primary_muscle_group.display_name,
            }
        return None

    def get_equipment(self, obj: Exercise) -> dict[str, Any] | None:
        """Retorna el equipamiento con name y displayName."""
        if obj.equipment:
            return {
                "name": obj.equipment.name,
                "displayName": obj.equipment.display_name,
            }
        return None

    def get_difficulty(self, obj: Exercise) -> dict[str, Any] | None:
        """Retorna la dificultad con name y displayName."""
        if obj.difficulty:
            return {
                "name": obj.difficulty.name,
                "displayName": obj.difficulty.display_name,
            }
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
    movementType = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primaryMuscleGroup = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    secondaryMuscleGroups = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    equipment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    difficulty = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imageUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    videoUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    isActive = serializers.BooleanField(required=False, default=True)

    def validate_name(self, value: str) -> str:
        """Valida que el nombre no esté vacío."""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value.strip()

    def validate_difficulty(self, value: str) -> str:
        """Valida que la dificultad exista y esté activa."""
        if not value or value.strip() == "":
            return None
        value = value.strip()
        if not Difficulty.objects.filter(name=value, is_active=True).exists():
            valid_difficulties = list(
                Difficulty.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise serializers.ValidationError(f"Debe ser uno de: {', '.join(valid_difficulties)}")
        return value

    def validate_secondaryMuscleGroups(self, value: list) -> list:
        """Valida que secondaryMuscleGroups sea un array de strings válidos."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Debe ser un array")
        valid_groups = list(
            MuscleGroup.objects.filter(is_active=True).values_list("name", flat=True)
        )
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
    movementType = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primaryMuscleGroup = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    secondaryMuscleGroups = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    equipment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    difficulty = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imageUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    videoUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    isActive = serializers.BooleanField(required=False)

    def validate_name(self, value: str) -> str:
        """Valida que el nombre no esté vacío si se proporciona."""
        if value and not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value.strip() if value else value

    def validate_movementType(self, value: str) -> str:
        """Valida que el tipo de movimiento exista y esté activo."""
        if not value or value.strip() == "":
            return None
        value = value.strip()
        if not MovementType.objects.filter(name=value, is_active=True).exists():
            valid_types = list(
                MovementType.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise serializers.ValidationError(
                f"Debe ser uno de los tipos activos: {', '.join(valid_types)}"
            )
        return value

    def validate_primaryMuscleGroup(self, value: str) -> str:
        """Valida que el grupo muscular exista y esté activo."""
        if not value or value.strip() == "":
            return None
        value = value.strip()
        if not MuscleGroup.objects.filter(name=value, is_active=True).exists():
            valid_groups = list(
                MuscleGroup.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise serializers.ValidationError(
                f"Debe ser uno de los grupos activos: {', '.join(valid_groups)}"
            )
        return value

    def validate_equipment(self, value: str) -> str:
        """Valida que el equipamiento exista y esté activo."""
        if not value or value.strip() == "":
            return None
        value = value.strip()
        if not Equipment.objects.filter(name=value, is_active=True).exists():
            valid_equipment = list(
                Equipment.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise serializers.ValidationError(
                f"Debe ser uno de los equipamientos activos: {', '.join(valid_equipment)}"
            )
        return value

    def validate_difficulty(self, value: str) -> str:
        """Valida que la dificultad exista y esté activa."""
        if not value or value.strip() == "":
            return None
        value = value.strip()
        if not Difficulty.objects.filter(name=value, is_active=True).exists():
            valid_difficulties = list(
                Difficulty.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise serializers.ValidationError(f"Debe ser uno de: {', '.join(valid_difficulties)}")
        return value

    def validate_secondaryMuscleGroups(self, value: list) -> list:
        """Valida que secondaryMuscleGroups sea un array de strings válidos."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Debe ser un array")
        valid_groups = list(
            MuscleGroup.objects.filter(is_active=True).values_list("name", flat=True)
        )
        for group in value:
            if not isinstance(group, str):
                raise serializers.ValidationError("Todos los elementos deben ser strings")
            if group not in valid_groups:
                raise serializers.ValidationError(
                    f"Cada elemento debe ser uno de: {', '.join(valid_groups)}"
                )
        return value
