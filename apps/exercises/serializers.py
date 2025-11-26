from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

from apps.exercises.models import Exercise

if TYPE_CHECKING:
    pass


class ExerciseSerializer(serializers.ModelSerializer):
    """Serializador para representar un ejercicio completo."""

    # Campos calculados
    createdBy = serializers.SerializerMethodField()
    movementType = serializers.CharField(source="movement_type", required=False, allow_null=True)
    primaryMuscleGroup = serializers.CharField(
        source="primary_muscle_group", required=False, allow_null=True
    )
    secondaryMuscleGroups = serializers.JSONField(required=False, allow_null=True)
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
        fields = [
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
        read_only_fields = ["id", "createdAt", "updatedAt"]

    def get_createdBy(self, obj: Exercise) -> Any:
        """Retorna el username o id del creador."""
        if obj.created_by:
            return obj.created_by.username
        return None


class ExerciseCreateSerializer(serializers.Serializer):
    """Serializador para crear un nuevo ejercicio."""

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
    """Serializador para actualizar un ejercicio existente."""

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

