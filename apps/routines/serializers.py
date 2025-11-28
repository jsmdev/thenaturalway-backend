from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

from apps.routines.models import Routine, Week, Day, Block, RoutineExercise

if TYPE_CHECKING:
    pass


# Serializadores para Routine
class RoutineSerializer(serializers.ModelSerializer):
    """Serializador para representar una rutina completa."""

    createdBy = serializers.SerializerMethodField()
    durationWeeks = serializers.IntegerField(
        source="duration_weeks", required=False, allow_null=True
    )
    durationMonths = serializers.IntegerField(
        source="duration_months", required=False, allow_null=True
    )
    isActive = serializers.BooleanField(source="is_active", required=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Routine
        fields = [
            "id",
            "name",
            "description",
            "durationWeeks",
            "durationMonths",
            "isActive",
            "createdBy",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "createdAt", "updatedAt"]

    def get_createdBy(self, obj: Routine) -> Any:
        """Retorna el username o id del creador."""
        if obj.created_by:
            return obj.created_by.username
        return None


class RoutineCreateSerializer(serializers.Serializer):
    """Serializador para crear una nueva rutina."""

    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    durationWeeks = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    durationMonths = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    isActive = serializers.BooleanField(required=False, default=True)

    def validate_name(self, value: str) -> str:
        """Valida que el nombre no esté vacío."""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value.strip()


class RoutineUpdateSerializer(serializers.Serializer):
    """Serializador para actualizar una rutina existente."""

    name = serializers.CharField(required=False, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    durationWeeks = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    durationMonths = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    isActive = serializers.BooleanField(required=False)

    def validate_name(self, value: str) -> str:
        """Valida que el nombre no esté vacío si se proporciona."""
        if value and not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value.strip() if value else value


# Serializadores para Week
class WeekSerializer(serializers.ModelSerializer):
    """Serializador para representar una semana."""

    routineId = serializers.IntegerField(source="routine_id", read_only=True)
    weekNumber = serializers.IntegerField(source="week_number")
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Week
        fields = ["id", "routineId", "weekNumber", "notes", "createdAt", "updatedAt"]
        read_only_fields = ["id", "routineId", "createdAt", "updatedAt"]


class WeekCreateSerializer(serializers.Serializer):
    """Serializador para crear una nueva semana."""

    weekNumber = serializers.IntegerField(required=True, min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


# Serializadores para Day
class DaySerializer(serializers.ModelSerializer):
    """Serializador para representar un día."""

    weekId = serializers.IntegerField(source="week_id", read_only=True)
    dayNumber = serializers.IntegerField(source="day_number")
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Day
        fields = [
            "id",
            "weekId",
            "dayNumber",
            "name",
            "notes",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "weekId", "createdAt", "updatedAt"]


class DayCreateSerializer(serializers.Serializer):
    """Serializador para crear un nuevo día."""

    dayNumber = serializers.IntegerField(required=True, min_value=1)
    name = serializers.CharField(required=False, max_length=255, allow_blank=True, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


# Serializadores para Block
class BlockSerializer(serializers.ModelSerializer):
    """Serializador para representar un bloque."""

    dayId = serializers.IntegerField(source="day_id", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Block
        fields = ["id", "dayId", "name", "order", "notes", "createdAt", "updatedAt"]
        read_only_fields = ["id", "dayId", "createdAt", "updatedAt"]


class BlockCreateSerializer(serializers.Serializer):
    """Serializador para crear un nuevo bloque."""

    name = serializers.CharField(required=True, max_length=255)
    order = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_name(self, value: str) -> str:
        """Valida que el nombre no esté vacío."""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value.strip()


# Serializadores para RoutineExercise
class RoutineExerciseSerializer(serializers.ModelSerializer):
    """Serializador para representar un ejercicio en rutina."""

    blockId = serializers.IntegerField(source="block_id", read_only=True)
    exerciseId = serializers.IntegerField(source="exercise_id", read_only=True)
    exerciseName = serializers.CharField(source="exercise.name", read_only=True)
    weightPercentage = serializers.DecimalField(
        source="weight_percentage", max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    restSeconds = serializers.IntegerField(source="rest_seconds", required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = RoutineExercise
        fields = [
            "id",
            "blockId",
            "exerciseId",
            "exerciseName",
            "order",
            "sets",
            "repetitions",
            "weight",
            "weightPercentage",
            "tempo",
            "restSeconds",
            "notes",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = [
            "id",
            "blockId",
            "exerciseId",
            "exerciseName",
            "createdAt",
            "updatedAt",
        ]


class RoutineExerciseCreateSerializer(serializers.Serializer):
    """Serializador para crear un nuevo ejercicio en rutina."""

    exerciseId = serializers.IntegerField(required=True, min_value=1)
    order = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    sets = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    repetitions = serializers.CharField(required=False, max_length=50, allow_blank=True, allow_null=True)
    weight = serializers.DecimalField(
        required=False, max_digits=8, decimal_places=2, allow_null=True, min_value=0
    )
    weightPercentage = serializers.DecimalField(
        required=False, max_digits=5, decimal_places=2, allow_null=True, min_value=0, max_value=100
    )
    tempo = serializers.CharField(required=False, max_length=50, allow_blank=True, allow_null=True)
    restSeconds = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


# Serializador completo con jerarquía anidada
class RoutineFullSerializer(serializers.ModelSerializer):
    """Serializador para representar una rutina completa con toda su jerarquía."""

    createdBy = serializers.SerializerMethodField()
    durationWeeks = serializers.IntegerField(source="duration_weeks", required=False, allow_null=True)
    durationMonths = serializers.IntegerField(source="duration_months", required=False, allow_null=True)
    isActive = serializers.BooleanField(source="is_active", required=False)
    weeks = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Routine
        fields = [
            "id",
            "name",
            "description",
            "durationWeeks",
            "durationMonths",
            "isActive",
            "createdBy",
            "weeks",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "createdAt", "updatedAt"]

    def get_createdBy(self, obj: Routine) -> Any:
        """Retorna el username o id del creador."""
        if obj.created_by:
            return obj.created_by.username
        return None

    def get_weeks(self, obj: Routine) -> list:
        """Retorna las semanas con su jerarquía completa."""
        weeks_data = []
        for week in obj.weeks.all():
            days_data = []
            for day in week.days.all():
                blocks_data = []
                for block in day.blocks.all():
                    exercises_data = []
                    for exercise in block.routine_exercises.all():
                        exercises_data.append(
                            {
                                "id": exercise.id,
                                "exerciseId": exercise.exercise_id,
                                "exerciseName": exercise.exercise.name,
                                "order": exercise.order,
                                "sets": exercise.sets,
                                "repetitions": exercise.repetitions,
                                "weight": float(exercise.weight) if exercise.weight else None,
                                "weightPercentage": (
                                    float(exercise.weight_percentage)
                                    if exercise.weight_percentage
                                    else None
                                ),
                                "tempo": exercise.tempo,
                                "restSeconds": exercise.rest_seconds,
                                "notes": exercise.notes,
                            }
                        )
                    blocks_data.append(
                        {
                            "id": block.id,
                            "name": block.name,
                            "order": block.order,
                            "notes": block.notes,
                            "exercises": exercises_data,
                        }
                    )
                days_data.append(
                    {
                        "id": day.id,
                        "dayNumber": day.day_number,
                        "name": day.name,
                        "notes": day.notes,
                        "blocks": blocks_data,
                    }
                )
            weeks_data.append(
                {
                    "id": week.id,
                    "weekNumber": week.week_number,
                    "notes": week.notes,
                    "days": days_data,
                }
            )
        return weeks_data

