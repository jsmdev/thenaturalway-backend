from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.exercises.models import Equipment, MovementType, MuscleGroup
from apps.exercises.repositories import (
    create_exercise_repository,
    delete_exercise_repository,
    get_exercise_by_id_repository,
    list_exercises_repository,
    update_exercise_repository,
)

if TYPE_CHECKING:
    from apps.exercises.models import Exercise
    from apps.users.models import User


def list_exercises_service(
    filters: dict[str, Any] | None = None,
    search: str | None = None,
    ordering: str | None = None,
    user: User | None = None,
) -> list[Exercise]:
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
            muscle_group_slug = filters["primaryMuscleGroup"]
            if not MuscleGroup.objects.filter(name=muscle_group_slug, is_active=True).exists():
                valid_groups = list(
                    MuscleGroup.objects.filter(is_active=True).values_list("name", flat=True)
                )
                raise ValidationError(
                    {
                        "primaryMuscleGroup": f"Debe ser uno de los grupos activos: {', '.join(valid_groups)}"
                    }
                )
            valid_filters["primaryMuscleGroup"] = muscle_group_slug

        if "equipment" in filters:
            equipment_slug = filters["equipment"]
            if not Equipment.objects.filter(name=equipment_slug, is_active=True).exists():
                valid_equipment = list(
                    Equipment.objects.filter(is_active=True).values_list("name", flat=True)
                )
                raise ValidationError(
                    {
                        "equipment": f"Debe ser uno de los equipamientos activos: {', '.join(valid_equipment)}"
                    }
                )
            valid_filters["equipment"] = equipment_slug

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
            except (ValueError, TypeError) as e:
                raise ValidationError({"createdBy": "Debe ser un número entero"}) from e

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


def create_exercise_service(validated_data: dict[str, Any], user: User | None = None) -> Exercise:
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

    # Convertir slugs a objetos ForeignKey si se proporcionan
    if validated_data.get("movementType"):
        movement_type_slug = validated_data["movementType"]
        try:
            movement_type = MovementType.objects.get(name=movement_type_slug, is_active=True)
            validated_data["movementType"] = movement_type
        except MovementType.DoesNotExist as e:
            valid_types = list(
                MovementType.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise ValidationError(
                {"movementType": f"Debe ser uno de los tipos activos: {', '.join(valid_types)}"}
            ) from e

    if validated_data.get("primaryMuscleGroup"):
        muscle_group_slug = validated_data["primaryMuscleGroup"]
        try:
            muscle_group = MuscleGroup.objects.get(name=muscle_group_slug, is_active=True)
            validated_data["primaryMuscleGroup"] = muscle_group
        except MuscleGroup.DoesNotExist as e:
            valid_groups = list(
                MuscleGroup.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise ValidationError(
                {
                    "primaryMuscleGroup": f"Debe ser uno de los grupos activos: {', '.join(valid_groups)}"
                }
            ) from e

    if validated_data.get("equipment"):
        equipment_slug = validated_data["equipment"]
        try:
            equipment = Equipment.objects.get(name=equipment_slug, is_active=True)
            validated_data["equipment"] = equipment
        except Equipment.DoesNotExist as e:
            valid_equipment = list(
                Equipment.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise ValidationError(
                {
                    "equipment": f"Debe ser uno de los equipamientos activos: {', '.join(valid_equipment)}"
                }
            ) from e

    if "difficulty" in validated_data:
        valid_difficulty = ["beginner", "intermediate", "advanced"]
        if validated_data["difficulty"] not in valid_difficulty:
            raise ValidationError({"difficulty": f"Debe ser uno de: {', '.join(valid_difficulty)}"})

    # Validar secondaryMuscleGroups si se proporciona
    if "secondaryMuscleGroups" in validated_data:
        if not isinstance(validated_data["secondaryMuscleGroups"], list):
            raise ValidationError({"secondaryMuscleGroups": "Debe ser un array de strings"})
        valid_secondary_groups = list(
            MuscleGroup.objects.filter(is_active=True).values_list("name", flat=True)
        )
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
    exercise_id: int, validated_data: dict[str, Any], user: User | None = None
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

    # Convertir slugs a objetos ForeignKey si se proporcionan
    if validated_data.get("movementType"):
        movement_type_slug = validated_data["movementType"]
        try:
            movement_type = MovementType.objects.get(name=movement_type_slug, is_active=True)
            validated_data["movementType"] = movement_type
        except MovementType.DoesNotExist as e:
            valid_types = list(
                MovementType.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise ValidationError(
                {"movementType": f"Debe ser uno de los tipos activos: {', '.join(valid_types)}"}
            ) from e

    if validated_data.get("primaryMuscleGroup"):
        muscle_group_slug = validated_data["primaryMuscleGroup"]
        try:
            muscle_group = MuscleGroup.objects.get(name=muscle_group_slug, is_active=True)
            validated_data["primaryMuscleGroup"] = muscle_group
        except MuscleGroup.DoesNotExist as e:
            valid_groups = list(
                MuscleGroup.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise ValidationError(
                {
                    "primaryMuscleGroup": f"Debe ser uno de los grupos activos: {', '.join(valid_groups)}"
                }
            ) from e

    if validated_data.get("equipment"):
        equipment_slug = validated_data["equipment"]
        try:
            equipment = Equipment.objects.get(name=equipment_slug, is_active=True)
            validated_data["equipment"] = equipment
        except Equipment.DoesNotExist as e:
            valid_equipment = list(
                Equipment.objects.filter(is_active=True).values_list("name", flat=True)
            )
            raise ValidationError(
                {
                    "equipment": f"Debe ser uno de los equipamientos activos: {', '.join(valid_equipment)}"
                }
            ) from e

    if "difficulty" in validated_data:
        valid_difficulty = ["beginner", "intermediate", "advanced"]
        if validated_data["difficulty"] not in valid_difficulty:
            raise ValidationError({"difficulty": f"Debe ser uno de: {', '.join(valid_difficulty)}"})

    # Validar secondaryMuscleGroups si se proporciona
    if "secondaryMuscleGroups" in validated_data:
        if not isinstance(validated_data["secondaryMuscleGroups"], list):
            raise ValidationError({"secondaryMuscleGroups": "Debe ser un array de strings"})
        valid_secondary_groups = list(
            MuscleGroup.objects.filter(is_active=True).values_list("name", flat=True)
        )
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
    updated_exercise = update_exercise_repository(exercise=exercise, validated_data=validated_data)

    return updated_exercise


def delete_exercise_service(exercise_id: int, user: User | None = None) -> Exercise:
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
