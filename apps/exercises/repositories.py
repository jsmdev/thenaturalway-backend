from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models import Q, QuerySet

from apps.exercises.models import Exercise

if TYPE_CHECKING:
    from apps.users.models import User


def list_exercises_repository(
    filters: dict[str, Any] | None = None,
    search: str | None = None,
    ordering: str | None = None,
) -> QuerySet[Exercise]:
    """
    Lista ejercicios con filtros, búsqueda y ordenamiento.

    Args:
        filters: Diccionario con filtros (primaryMuscleGroup, equipment, difficulty, isActive, createdBy)
        search: Texto para búsqueda en name y description
        ordering: Campo para ordenamiento (por defecto 'name')

    Returns:
        QuerySet de ejercicios filtrados
    """
    queryset = Exercise.objects.select_related("created_by").all()

    # Aplicar filtros
    if filters:
        if filters.get("primaryMuscleGroup"):
            queryset = queryset.filter(primary_muscle_group=filters["primaryMuscleGroup"])
        if filters.get("equipment"):
            queryset = queryset.filter(equipment=filters["equipment"])
        if filters.get("difficulty"):
            queryset = queryset.filter(difficulty=filters["difficulty"])
        if filters.get("isActive") is not None:
            queryset = queryset.filter(is_active=filters["isActive"])
        if filters.get("createdBy"):
            queryset = queryset.filter(created_by_id=filters["createdBy"])

    # Aplicar búsqueda
    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

    # Aplicar ordenamiento
    queryset = queryset.order_by(ordering) if ordering else queryset.order_by("name")

    return queryset


def get_exercise_by_id_repository(exercise_id: int) -> Exercise | None:
    """
    Obtiene un ejercicio por su ID.

    Args:
        exercise_id: ID del ejercicio

    Returns:
        Exercise o None si no existe
    """
    try:
        return Exercise.objects.select_related("created_by").get(id=exercise_id)
    except Exercise.DoesNotExist:
        return None


def create_exercise_repository(
    validated_data: dict[str, Any], user: User | None = None
) -> Exercise:
    """
    Crea un nuevo ejercicio.

    Args:
        validated_data: Datos validados del ejercicio
        user: Usuario que crea el ejercicio

    Returns:
        Exercise creado
    """
    # Mapear nombres de dominio a nombres de modelo
    exercise_data = {
        "name": validated_data.get("name"),
        "description": validated_data.get("description"),
        "movement_type": validated_data.get("movementType"),
        "primary_muscle_group": validated_data.get("primaryMuscleGroup"),
        "secondary_muscle_groups": validated_data.get("secondaryMuscleGroups", []),
        "equipment": validated_data.get("equipment"),
        "difficulty": validated_data.get("difficulty"),
        "instructions": validated_data.get("instructions"),
        "image_url": validated_data.get("imageUrl"),
        "video_url": validated_data.get("videoUrl"),
        "is_active": validated_data.get("isActive", True),
        "created_by": user,
    }

    # Eliminar None values
    exercise_data = {k: v for k, v in exercise_data.items() if v is not None}

    return Exercise.objects.create(**exercise_data)


def update_exercise_repository(exercise: Exercise, validated_data: dict[str, Any]) -> Exercise:
    """
    Actualiza un ejercicio existente.

    Args:
        exercise: Instancia del ejercicio a actualizar
        validated_data: Datos validados para actualizar

    Returns:
        Exercise actualizado
    """
    # Mapear nombres de dominio a nombres de modelo
    if "name" in validated_data:
        exercise.name = validated_data["name"]
    if "description" in validated_data:
        exercise.description = validated_data["description"]
    if "movementType" in validated_data:
        exercise.movement_type = validated_data["movementType"]
    if "primaryMuscleGroup" in validated_data:
        exercise.primary_muscle_group = validated_data["primaryMuscleGroup"]
    if "secondaryMuscleGroups" in validated_data:
        exercise.secondary_muscle_groups = validated_data["secondaryMuscleGroups"]
    if "equipment" in validated_data:
        exercise.equipment = validated_data["equipment"]
    if "difficulty" in validated_data:
        exercise.difficulty = validated_data["difficulty"]
    if "instructions" in validated_data:
        exercise.instructions = validated_data["instructions"]
    if "imageUrl" in validated_data:
        exercise.image_url = validated_data["imageUrl"]
    if "videoUrl" in validated_data:
        exercise.video_url = validated_data["videoUrl"]
    if "isActive" in validated_data:
        exercise.is_active = validated_data["isActive"]

    exercise.save()
    return exercise


def delete_exercise_repository(exercise: Exercise) -> Exercise:
    """
    Realiza soft delete de un ejercicio (marca isActive=False).

    Args:
        exercise: Instancia del ejercicio a eliminar

    Returns:
        Exercise con isActive=False
    """
    exercise.is_active = False
    exercise.save()
    return exercise
