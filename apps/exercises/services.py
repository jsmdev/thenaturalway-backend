from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Any, List

from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied

from apps.exercises.repositories import (
    list_exercises_repository,
    get_exercise_by_id_repository,
    create_exercise_repository,
    update_exercise_repository,
    delete_exercise_repository,
)

if TYPE_CHECKING:
    from apps.users.models import User
    from apps.exercises.models import Exercise


def list_exercises_service(
    filters: Optional[Dict[str, Any]] = None,
    search: Optional[str] = None,
    ordering: Optional[str] = None,
    user: Optional[User] = None,
) -> List[Exercise]:
    """
    Servicio para listar ejercicios con filtros y búsqueda.

    Args:
        filters: Diccionario con filtros
        search: Texto para búsqueda
        ordering: Campo para ordenamiento
        user: Usuario autenticado (opcional)

    Returns:
        Lista de ejercicios
    """
    # Validar filtros si se proporcionan
    if filters:
        valid_filters = {}
        if "primaryMuscleGroup" in filters:
            valid_primary_muscle_groups = [
                "chest",
                "back",
                "shoulders",
                "arms",
                "legs",
                "core",
                "full_body",
                "other",
            ]
            if filters["primaryMuscleGroup"] not in valid_primary_muscle_groups:
                raise ValidationError(
                    {
                        "primaryMuscleGroup": f"Debe ser uno de: {', '.join(valid_primary_muscle_groups)}"
                    }
                )
            valid_filters["primaryMuscleGroup"] = filters["primaryMuscleGroup"]

        if "equipment" in filters:
            valid_equipment = [
                "barbell",
                "dumbbell",
                "cable",
                "machine",
                "bodyweight",
                "kettlebell",
                "other",
            ]
            if filters["equipment"] not in valid_equipment:
                raise ValidationError(
                    {"equipment": f"Debe ser uno de: {', '.join(valid_equipment)}"}
                )
            valid_filters["equipment"] = filters["equipment"]

        if "difficulty" in filters:
            valid_difficulty = ["beginner", "intermediate", "advanced"]
            if filters["difficulty"] not in valid_difficulty:
                raise ValidationError(
                    {"difficulty": f"Debe ser uno de: {', '.join(valid_difficulty)}"}
                )
            valid_filters["difficulty"] = filters["difficulty"]

        if "isActive" in filters:
            if not isinstance(filters["isActive"], bool):
                # Intentar convertir string a bool
                is_active_str = str(filters["isActive"]).lower()
                if is_active_str in ["true", "1", "yes"]:
                    valid_filters["isActive"] = True
                elif is_active_str in ["false", "0", "no"]:
                    valid_filters["isActive"] = False
                else:
                    raise ValidationError({"isActive": "Debe ser true o false"})
            else:
                valid_filters["isActive"] = filters["isActive"]

        if "createdBy" in filters:
            try:
                valid_filters["createdBy"] = int(filters["createdBy"])
            except (ValueError, TypeError):
                raise ValidationError({"createdBy": "Debe ser un número entero"})

        filters = valid_filters

    # Llamar al repositorio
    queryset = list_exercises_repository(filters=filters, search=search, ordering=ordering)

    return list(queryset)


def get_exercise_service(exercise_id: int) -> Exercise:
    """
    Servicio para obtener un ejercicio por ID.

    Args:
        exercise_id: ID del ejercicio

    Returns:
        Exercise

    Raises:
        NotFound: Si el ejercicio no existe
    """
    exercise = get_exercise_by_id_repository(exercise_id=exercise_id)

    if not exercise:
        raise NotFound("Ejercicio no encontrado")

    return exercise


def create_exercise_service(validated_data: Dict[str, Any], user: Optional[User] = None) -> Exercise:
    """
    Servicio para crear un nuevo ejercicio.

    Args:
        validated_data: Datos validados del ejercicio
        user: Usuario que crea el ejercicio

    Returns:
        Exercise creado

    Raises:
        ValidationError: Si los datos no son válidos
    """
    # Validar que name esté presente
    if not validated_data.get("name"):
        raise ValidationError({"name": "El nombre es requerido"})

    # Validar enums si se proporcionan
    if "movementType" in validated_data:
        valid_movement_types = ["push", "pull", "squat", "hinge", "carry", "other"]
        if validated_data["movementType"] not in valid_movement_types:
            raise ValidationError(
                {
                    "movementType": f"Debe ser uno de: {', '.join(valid_movement_types)}"
                }
            )

    if "primaryMuscleGroup" in validated_data:
        valid_primary_muscle_groups = [
            "chest",
            "back",
            "shoulders",
            "arms",
            "legs",
            "core",
            "full_body",
            "other",
        ]
        if validated_data["primaryMuscleGroup"] not in valid_primary_muscle_groups:
            raise ValidationError(
                {
                    "primaryMuscleGroup": f"Debe ser uno de: {', '.join(valid_primary_muscle_groups)}"
                }
            )

    if "equipment" in validated_data:
        valid_equipment = [
            "barbell",
            "dumbbell",
            "cable",
            "machine",
            "bodyweight",
            "kettlebell",
            "other",
        ]
        if validated_data["equipment"] not in valid_equipment:
            raise ValidationError(
                {"equipment": f"Debe ser uno de: {', '.join(valid_equipment)}"}
            )

    if "difficulty" in validated_data:
        valid_difficulty = ["beginner", "intermediate", "advanced"]
        if validated_data["difficulty"] not in valid_difficulty:
            raise ValidationError(
                {"difficulty": f"Debe ser uno de: {', '.join(valid_difficulty)}"}
            )

    # Validar secondaryMuscleGroups si se proporciona
    if "secondaryMuscleGroups" in validated_data:
        if not isinstance(validated_data["secondaryMuscleGroups"], list):
            raise ValidationError(
                {"secondaryMuscleGroups": "Debe ser un array de strings"}
            )
        valid_secondary_groups = [
            "chest",
            "back",
            "shoulders",
            "arms",
            "legs",
            "core",
            "full_body",
            "other",
        ]
        for group in validated_data["secondaryMuscleGroups"]:
            if not isinstance(group, str):
                raise ValidationError(
                    {"secondaryMuscleGroups": "Todos los elementos deben ser strings"}
                )
            if group not in valid_secondary_groups:
                raise ValidationError(
                    {
                        "secondaryMuscleGroups": f"Cada elemento debe ser uno de: {', '.join(valid_secondary_groups)}"
                    }
                )

    # Crear ejercicio
    exercise = create_exercise_repository(validated_data=validated_data, user=user)

    return exercise


def update_exercise_service(
    exercise_id: int, validated_data: Dict[str, Any], user: Optional[User] = None
) -> Exercise:
    """
    Servicio para actualizar un ejercicio existente.

    Args:
        exercise_id: ID del ejercicio a actualizar
        validated_data: Datos validados para actualizar
        user: Usuario que intenta actualizar

    Returns:
        Exercise actualizado

    Raises:
        NotFound: Si el ejercicio no existe
        PermissionDenied: Si el usuario no es el creador
        ValidationError: Si los datos no son válidos
    """
    # Obtener ejercicio
    exercise = get_exercise_by_id_repository(exercise_id=exercise_id)

    if not exercise:
        raise NotFound("Ejercicio no encontrado")

    # Verificar permisos (solo el creador puede actualizar)
    if user and exercise.created_by and exercise.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede actualizar este ejercicio")

    # Validar enums si se proporcionan
    if "movementType" in validated_data:
        valid_movement_types = ["push", "pull", "squat", "hinge", "carry", "other"]
        if validated_data["movementType"] not in valid_movement_types:
            raise ValidationError(
                {
                    "movementType": f"Debe ser uno de: {', '.join(valid_movement_types)}"
                }
            )

    if "primaryMuscleGroup" in validated_data:
        valid_primary_muscle_groups = [
            "chest",
            "back",
            "shoulders",
            "arms",
            "legs",
            "core",
            "full_body",
            "other",
        ]
        if validated_data["primaryMuscleGroup"] not in valid_primary_muscle_groups:
            raise ValidationError(
                {
                    "primaryMuscleGroup": f"Debe ser uno de: {', '.join(valid_primary_muscle_groups)}"
                }
            )

    if "equipment" in validated_data:
        valid_equipment = [
            "barbell",
            "dumbbell",
            "cable",
            "machine",
            "bodyweight",
            "kettlebell",
            "other",
        ]
        if validated_data["equipment"] not in valid_equipment:
            raise ValidationError(
                {"equipment": f"Debe ser uno de: {', '.join(valid_equipment)}"}
            )

    if "difficulty" in validated_data:
        valid_difficulty = ["beginner", "intermediate", "advanced"]
        if validated_data["difficulty"] not in valid_difficulty:
            raise ValidationError(
                {"difficulty": f"Debe ser uno de: {', '.join(valid_difficulty)}"}
            )

    # Validar secondaryMuscleGroups si se proporciona
    if "secondaryMuscleGroups" in validated_data:
        if not isinstance(validated_data["secondaryMuscleGroups"], list):
            raise ValidationError(
                {"secondaryMuscleGroups": "Debe ser un array de strings"}
            )
        valid_secondary_groups = [
            "chest",
            "back",
            "shoulders",
            "arms",
            "legs",
            "core",
            "full_body",
            "other",
        ]
        for group in validated_data["secondaryMuscleGroups"]:
            if not isinstance(group, str):
                raise ValidationError(
                    {"secondaryMuscleGroups": "Todos los elementos deben ser strings"}
                )
            if group not in valid_secondary_groups:
                raise ValidationError(
                    {
                        "secondaryMuscleGroups": f"Cada elemento debe ser uno de: {', '.join(valid_secondary_groups)}"
                    }
                )

    # Actualizar ejercicio
    updated_exercise = update_exercise_repository(
        exercise=exercise, validated_data=validated_data
    )

    return updated_exercise


def delete_exercise_service(exercise_id: int, user: Optional[User] = None) -> Exercise:
    """
    Servicio para eliminar un ejercicio (soft delete).

    Args:
        exercise_id: ID del ejercicio a eliminar
        user: Usuario que intenta eliminar

    Returns:
        Exercise con isActive=False

    Raises:
        NotFound: Si el ejercicio no existe
        PermissionDenied: Si el usuario no es el creador
    """
    # Obtener ejercicio
    exercise = get_exercise_by_id_repository(exercise_id=exercise_id)

    if not exercise:
        raise NotFound("Ejercicio no encontrado")

    # Verificar permisos (solo el creador puede eliminar)
    if user and exercise.created_by and exercise.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede eliminar este ejercicio")

    # Realizar soft delete
    deleted_exercise = delete_exercise_repository(exercise=exercise)

    return deleted_exercise

