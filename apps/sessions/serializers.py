from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

from apps.sessions.models import Session, SessionExercise

if TYPE_CHECKING:
    pass


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializador para representar una sesión completa.

    Este serializador se usa para representar sesiones en respuestas de la API.
    Incluye todos los campos del modelo con nombres en camelCase para la API.
    """

    # Campos calculados
    userId = serializers.IntegerField(source="user.id", read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)
    routineId = serializers.IntegerField(source="routine.id", required=False, allow_null=True)
    routine = serializers.CharField(source="routine.name", required=False, allow_null=True, read_only=True)
    startTime = serializers.DateTimeField(source="start_time", required=False, allow_null=True)
    endTime = serializers.DateTimeField(source="end_time", required=False, allow_null=True)
    durationMinutes = serializers.IntegerField(source="duration_minutes", required=False, allow_null=True)
    energyLevel = serializers.CharField(source="energy_level", required=False, allow_null=True)
    sleepHours = serializers.DecimalField(source="sleep_hours", max_digits=4, decimal_places=2, required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "userId",
            "user",
            "routineId",
            "routine",
            "date",
            "startTime",
            "endTime",
            "durationMinutes",
            "notes",
            "rpe",
            "energyLevel",
            "sleepHours",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "userId", "user", "createdAt", "updatedAt"]


class SessionCreateSerializer(serializers.Serializer):
    """
    Serializador para crear una nueva sesión.

    Campos requeridos:
    - date (date): Fecha de la sesión

    Campos opcionales:
    - routineId (int): ID de la rutina a la que vincular
    - startTime (datetime): Hora de inicio
    - endTime (datetime): Hora de finalización
    - durationMinutes (int): Duración en minutos (se calcula automáticamente si hay startTime y endTime)
    - notes (str): Notas generales
    - rpe (int): Rate of Perceived Exertion (1-10)
    - energyLevel (str): Nivel de energía
    - sleepHours (decimal): Horas de sueño la noche anterior
    """

    date = serializers.DateField(required=True)
    routineId = serializers.IntegerField(required=False, allow_null=True)
    startTime = serializers.DateTimeField(required=False, allow_null=True)
    endTime = serializers.DateTimeField(required=False, allow_null=True)
    durationMinutes = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    rpe = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=10)
    energyLevel = serializers.ChoiceField(
        choices=Session.ENERGY_LEVEL_CHOICES, required=False, allow_null=True
    )
    sleepHours = serializers.DecimalField(
        max_digits=4, decimal_places=2, required=False, allow_null=True, min_value=0
    )

    def validate_rpe(self, value: int) -> int:
        """Valida que RPE esté entre 1 y 10."""
        if value is not None and (value < 1 or value > 10):
            raise serializers.ValidationError("RPE debe estar entre 1 y 10")
        return value


class SessionUpdateSerializer(serializers.Serializer):
    """
    Serializador para actualizar una sesión existente.

    Todos los campos son opcionales.
    """

    date = serializers.DateField(required=False)
    routineId = serializers.IntegerField(required=False, allow_null=True)
    startTime = serializers.DateTimeField(required=False, allow_null=True)
    endTime = serializers.DateTimeField(required=False, allow_null=True)
    durationMinutes = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    rpe = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=10)
    energyLevel = serializers.ChoiceField(
        choices=Session.ENERGY_LEVEL_CHOICES, required=False, allow_null=True
    )
    sleepHours = serializers.DecimalField(
        max_digits=4, decimal_places=2, required=False, allow_null=True, min_value=0
    )

    def validate_rpe(self, value: int) -> int:
        """Valida que RPE esté entre 1 y 10."""
        if value is not None and (value < 1 or value > 10):
            raise serializers.ValidationError("RPE debe estar entre 1 y 10")
        return value


class SessionExerciseSerializer(serializers.ModelSerializer):
    """
    Serializador para representar un ejercicio de sesión completo.
    """

    exerciseId = serializers.IntegerField(source="exercise.id", read_only=True)
    exercise = serializers.SerializerMethodField()
    sessionId = serializers.IntegerField(source="session.id", read_only=True)
    setsCompleted = serializers.IntegerField(source="sets_completed", required=False, allow_null=True)
    restSeconds = serializers.IntegerField(source="rest_seconds", required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = SessionExercise
        fields = [
            "id",
            "sessionId",
            "exerciseId",
            "exercise",
            "order",
            "setsCompleted",
            "repetitions",
            "weight",
            "rpe",
            "restSeconds",
            "notes",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "sessionId", "exerciseId", "createdAt", "updatedAt"]

    def get_exercise(self, obj: SessionExercise) -> dict[str, Any]:
        """Retorna información básica del ejercicio."""
        if obj.exercise:
            return {
                "id": obj.exercise.id,
                "name": obj.exercise.name,
                "primaryMuscleGroup": obj.exercise.primary_muscle_group,
            }
        return None


class SessionFullSerializer(serializers.ModelSerializer):
    """
    Serializador para representar una sesión completa con ejercicios asociados.
    """

    userId = serializers.IntegerField(source="user.id", read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)
    routineId = serializers.IntegerField(source="routine.id", required=False, allow_null=True)
    routine = serializers.CharField(source="routine.name", required=False, allow_null=True, read_only=True)
    startTime = serializers.DateTimeField(source="start_time", required=False, allow_null=True)
    endTime = serializers.DateTimeField(source="end_time", required=False, allow_null=True)
    durationMinutes = serializers.IntegerField(source="duration_minutes", required=False, allow_null=True)
    energyLevel = serializers.CharField(source="energy_level", required=False, allow_null=True)
    sleepHours = serializers.DecimalField(source="sleep_hours", max_digits=4, decimal_places=2, required=False, allow_null=True)
    sessionExercises = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "userId",
            "user",
            "routineId",
            "routine",
            "date",
            "startTime",
            "endTime",
            "durationMinutes",
            "notes",
            "rpe",
            "energyLevel",
            "sleepHours",
            "sessionExercises",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "userId", "user", "createdAt", "updatedAt"]

    def get_sessionExercises(self, obj: Session) -> list[dict[str, Any]]:
        """Retorna la lista de ejercicios de la sesión."""
        exercises = obj.session_exercises.select_related("exercise").all()
        return SessionExerciseSerializer(exercises, many=True).data


class SessionExerciseCreateSerializer(serializers.Serializer):
    """
    Serializador para crear un nuevo ejercicio en una sesión.

    Campos requeridos:
    - exerciseId (int): ID del ejercicio

    Campos opcionales:
    - order (int): Orden del ejercicio en la sesión
    - setsCompleted (int): Número de series completadas
    - repetitions (str): Repeticiones realizadas
    - weight (decimal): Peso utilizado en kilogramos
    - rpe (int): Rate of Perceived Exertion (1-10)
    - restSeconds (int): Tiempo de descanso en segundos
    - notes (str): Notas específicas
    """

    exerciseId = serializers.IntegerField(required=True)
    order = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    setsCompleted = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    repetitions = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    weight = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True, min_value=0
    )
    rpe = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=10)
    restSeconds = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_rpe(self, value: int) -> int:
        """Valida que RPE esté entre 1 y 10."""
        if value is not None and (value < 1 or value > 10):
            raise serializers.ValidationError("RPE debe estar entre 1 y 10")
        return value


class SessionExerciseUpdateSerializer(serializers.Serializer):
    """
    Serializador para actualizar un ejercicio de sesión existente.

    Todos los campos son opcionales.
    """

    exerciseId = serializers.IntegerField(required=False)
    order = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    setsCompleted = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    repetitions = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    weight = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True, min_value=0
    )
    rpe = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=10)
    restSeconds = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_rpe(self, value: int) -> int:
        """Valida que RPE esté entre 1 y 10."""
        if value is not None and (value < 1 or value > 10):
            raise serializers.ValidationError("RPE debe estar entre 1 y 10")
        return value

