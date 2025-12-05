from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.exercises.repositories import get_exercise_by_id_repository
from apps.routines.models import Day, Week
from apps.routines.repositories import (
    create_block_repository,
    create_day_repository,
    create_routine_exercise_repository,
    create_routine_repository,
    create_week_repository,
    delete_block_repository,
    delete_day_repository,
    delete_routine_exercise_repository,
    delete_routine_repository,
    delete_week_repository,
    get_block_by_id_repository,
    get_day_by_id_repository,
    get_routine_by_id_repository,
    get_routine_exercise_by_id_repository,
    get_routine_full_repository,
    get_week_by_id_repository,
    list_routines_repository,
    update_block_repository,
    update_day_repository,
    update_routine_exercise_repository,
    update_routine_repository,
    update_week_repository,
)

if TYPE_CHECKING:
    from apps.routines.models import Block, Day, Routine, RoutineExercise, Week
    from apps.users.models import User


# Servicios para Routine
def list_routines_service(user: User) -> list[Routine]:
    """
    Servicio para listar rutinas activas del usuario autenticado.

    Args:
        user: Usuario autenticado

    Returns:
        Lista de rutinas activas del usuario
    """
    queryset = list_routines_repository(user=user, filters={"isActive": True})
    return list(queryset)


def get_routine_service(routine_id: int, user: User) -> Routine:
    """
    Servicio para obtener una rutina por ID.

    Args:
        routine_id: ID de la rutina
        user: Usuario autenticado

    Returns:
        Routine

    Raises:
        NotFound: Si la rutina no existe o no pertenece al usuario
    """
    routine = get_routine_by_id_repository(routine_id=routine_id)

    if not routine:
        raise NotFound("Rutina no encontrada")

    # Verificar que la rutina pertenece al usuario
    if routine.created_by.id != user.id:
        raise NotFound("Rutina no encontrada")

    return routine


def create_routine_service(validated_data: dict[str, Any], user: User) -> Routine:
    """
    Servicio para crear una nueva rutina.

    Args:
        validated_data: Datos validados de la rutina
        user: Usuario que crea la rutina

    Returns:
        Routine creada

    Raises:
        ValidationError: Si los datos no son válidos
    """
    # Validar que name esté presente
    if not validated_data.get("name"):
        raise ValidationError({"name": "El nombre es requerido"})

    # Crear rutina
    routine = create_routine_repository(validated_data=validated_data, user=user)

    return routine


def update_routine_service(routine_id: int, validated_data: dict[str, Any], user: User) -> Routine:
    """
    Servicio para actualizar una rutina existente.

    Args:
        routine_id: ID de la rutina a actualizar
        validated_data: Datos validados para actualizar
        user: Usuario que intenta actualizar

    Returns:
        Routine actualizada

    Raises:
        NotFound: Si la rutina no existe
        PermissionDenied: Si el usuario no es el creador
    """
    # Obtener rutina
    routine = get_routine_by_id_repository(routine_id=routine_id)

    if not routine:
        raise NotFound("Rutina no encontrada")

    # Verificar permisos (solo el creador puede actualizar)
    if routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede actualizar esta rutina")

    # Actualizar rutina
    updated_routine = update_routine_repository(routine=routine, validated_data=validated_data)

    return updated_routine


def delete_routine_service(routine_id: int, user: User) -> Routine:
    """
    Servicio para eliminar una rutina (soft delete).

    Args:
        routine_id: ID de la rutina a eliminar
        user: Usuario que intenta eliminar

    Returns:
        Routine con isActive=False

    Raises:
        NotFound: Si la rutina no existe
        PermissionDenied: Si el usuario no es el creador
    """
    # Obtener rutina
    routine = get_routine_by_id_repository(routine_id=routine_id)

    if not routine:
        raise NotFound("Rutina no encontrada")

    # Verificar permisos (solo el creador puede eliminar)
    if routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede eliminar esta rutina")

    # Realizar soft delete
    deleted_routine = delete_routine_repository(routine=routine)

    return deleted_routine


# Servicios para Week
def create_week_service(routine_id: int, validated_data: dict[str, Any], user: User) -> Week:
    """
    Servicio para crear una nueva semana.

    Args:
        routine_id: ID de la rutina
        validated_data: Datos validados de la semana
        user: Usuario autenticado

    Returns:
        Week creada

    Raises:
        NotFound: Si la rutina no existe o no pertenece al usuario
        ValidationError: Si weekNumber no es único por rutina
    """
    # Verificar que la rutina existe y pertenece al usuario
    routine = get_routine_by_id_repository(routine_id=routine_id)

    if not routine:
        raise NotFound("Rutina no encontrada")

    if routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede añadir semanas a esta rutina")

    # Validar weekNumber único
    week_number = validated_data.get("weekNumber")
    if week_number is not None:
        existing = Week.objects.filter(routine_id=routine_id, week_number=week_number).exists()
        if existing:
            raise ValidationError(
                {"weekNumber": "Ya existe una semana con este número en esta rutina"}
            )

    # Crear semana
    week = create_week_repository(routine_id=routine_id, validated_data=validated_data)

    return week


def update_week_service(week_id: int, validated_data: dict[str, Any], user: User) -> Week:
    """
    Servicio para actualizar una semana existente.

    Args:
        week_id: ID de la semana a actualizar
        validated_data: Datos validados para actualizar
        user: Usuario que intenta actualizar

    Returns:
        Week actualizada

    Raises:
        NotFound: Si la semana no existe
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Obtener semana
    week = get_week_by_id_repository(week_id=week_id)

    if not week:
        raise NotFound("Semana no encontrada")

    # Verificar permisos (solo el creador de la rutina puede actualizar)
    if week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede actualizar esta semana")

    # Validar weekNumber único si se actualiza
    if "weekNumber" in validated_data:
        existing = Week.objects.filter(
            routine=week.routine, week_number=validated_data["weekNumber"]
        ).exclude(pk=week_id)
        if existing.exists():
            raise ValidationError(
                {"weekNumber": "Ya existe una semana con este número en esta rutina"}
            )

    # Actualizar semana
    updated_week = update_week_repository(week=week, validated_data=validated_data)

    return updated_week


def delete_week_service(week_id: int, user: User) -> None:
    """
    Servicio para eliminar una semana.

    Args:
        week_id: ID de la semana a eliminar
        user: Usuario que intenta eliminar

    Raises:
        NotFound: Si la semana no existe
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Obtener semana
    week = get_week_by_id_repository(week_id=week_id)

    if not week:
        raise NotFound("Semana no encontrada")

    # Verificar permisos
    if week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede eliminar esta semana")

    # Eliminar semana (CASCADE eliminará días, bloques y ejercicios)
    delete_week_repository(week=week)


# Servicios para Day
def create_day_service(week_id: int, validated_data: dict[str, Any], user: User) -> Day:
    """
    Servicio para crear un nuevo día.

    Args:
        week_id: ID de la semana
        validated_data: Datos validados del día
        user: Usuario autenticado

    Returns:
        Day creado

    Raises:
        NotFound: Si la semana no existe o no pertenece a rutina del usuario
        ValidationError: Si dayNumber no es único por semana
    """
    # Verificar que la semana existe y pertenece a rutina del usuario
    week = get_week_by_id_repository(week_id=week_id)

    if not week:
        raise NotFound("Semana no encontrada")

    if week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede añadir días a esta rutina")

    # Validar dayNumber único
    day_number = validated_data.get("dayNumber")
    if day_number is not None:
        existing = Day.objects.filter(week_id=week_id, day_number=day_number).exists()
        if existing:
            raise ValidationError({"dayNumber": "Ya existe un día con este número en esta semana"})

    # Crear día
    day = create_day_repository(week_id=week_id, validated_data=validated_data)

    return day


def update_day_service(day_id: int, validated_data: dict[str, Any], user: User) -> Day:
    """
    Servicio para actualizar un día existente.

    Args:
        day_id: ID del día a actualizar
        validated_data: Datos validados para actualizar
        user: Usuario que intenta actualizar

    Returns:
        Day actualizado

    Raises:
        NotFound: Si el día no existe
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Obtener día
    day = get_day_by_id_repository(day_id=day_id)

    if not day:
        raise NotFound("Día no encontrado")

    # Verificar permisos
    if day.week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede actualizar este día")

    # Validar dayNumber único si se actualiza
    if "dayNumber" in validated_data:
        existing = Day.objects.filter(
            week=day.week, day_number=validated_data["dayNumber"]
        ).exclude(pk=day_id)
        if existing.exists():
            raise ValidationError({"dayNumber": "Ya existe un día con este número en esta semana"})

    # Actualizar día
    updated_day = update_day_repository(day=day, validated_data=validated_data)

    return updated_day


def delete_day_service(day_id: int, user: User) -> None:
    """
    Servicio para eliminar un día.

    Args:
        day_id: ID del día a eliminar
        user: Usuario que intenta eliminar

    Raises:
        NotFound: Si el día no existe
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Obtener día
    day = get_day_by_id_repository(day_id=day_id)

    if not day:
        raise NotFound("Día no encontrado")

    # Verificar permisos
    if day.week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede eliminar este día")

    # Eliminar día (CASCADE eliminará bloques y ejercicios)
    delete_day_repository(day=day)


# Servicios para Block
def create_block_service(day_id: int, validated_data: dict[str, Any], user: User) -> Block:
    """
    Servicio para crear un nuevo bloque.

    Args:
        day_id: ID del día
        validated_data: Datos validados del bloque
        user: Usuario autenticado

    Returns:
        Block creado

    Raises:
        NotFound: Si el día no existe o no pertenece a rutina del usuario
    """
    # Verificar que el día existe y pertenece a rutina del usuario
    day = get_day_by_id_repository(day_id=day_id)

    if not day:
        raise NotFound("Día no encontrado")

    if day.week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede añadir bloques a esta rutina")

    # Crear bloque (order se asigna automáticamente si no se proporciona)
    block = create_block_repository(day_id=day_id, validated_data=validated_data)

    return block


def update_block_service(block_id: int, validated_data: dict[str, Any], user: User) -> Block:
    """
    Servicio para actualizar un bloque existente.

    Args:
        block_id: ID del bloque a actualizar
        validated_data: Datos validados para actualizar
        user: Usuario que intenta actualizar

    Returns:
        Block actualizado

    Raises:
        NotFound: Si el bloque no existe
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Obtener bloque
    block = get_block_by_id_repository(block_id=block_id)

    if not block:
        raise NotFound("Bloque no encontrado")

    # Verificar permisos
    if block.day.week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede actualizar este bloque")

    # Actualizar bloque
    updated_block = update_block_repository(block=block, validated_data=validated_data)

    return updated_block


def delete_block_service(block_id: int, user: User) -> None:
    """
    Servicio para eliminar un bloque.

    Args:
        block_id: ID del bloque a eliminar
        user: Usuario que intenta eliminar

    Raises:
        NotFound: Si el bloque no existe
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Obtener bloque
    block = get_block_by_id_repository(block_id=block_id)

    if not block:
        raise NotFound("Bloque no encontrado")

    # Verificar permisos
    if block.day.week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede eliminar este bloque")

    # Eliminar bloque (CASCADE eliminará ejercicios)
    delete_block_repository(block=block)


# Servicios para RoutineExercise
def create_routine_exercise_service(
    block_id: int, exercise_id: int, validated_data: dict[str, Any], user: User
) -> RoutineExercise:
    """
    Servicio para crear un nuevo ejercicio en rutina.

    Args:
        block_id: ID del bloque
        exercise_id: ID del ejercicio de la biblioteca
        validated_data: Datos validados del ejercicio en rutina
        user: Usuario autenticado

    Returns:
        RoutineExercise creado

    Raises:
        NotFound: Si el bloque o el ejercicio no existen
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Verificar que el bloque existe y pertenece a rutina del usuario
    block = get_block_by_id_repository(block_id=block_id)

    if not block:
        raise NotFound("Bloque no encontrado")

    if block.day.week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede añadir ejercicios a esta rutina")

    # Verificar que el ejercicio existe
    exercise = get_exercise_by_id_repository(exercise_id=exercise_id)

    if not exercise:
        raise NotFound("Ejercicio no encontrado")

    # Crear ejercicio en rutina (order se asigna automáticamente si no se proporciona)
    routine_exercise = create_routine_exercise_repository(
        block_id=block_id, exercise_id=exercise_id, validated_data=validated_data
    )

    return routine_exercise


def update_routine_exercise_service(
    routine_exercise_id: int, validated_data: dict[str, Any], user: User
) -> RoutineExercise:
    """
    Servicio para actualizar un ejercicio en rutina existente.

    Args:
        routine_exercise_id: ID del ejercicio en rutina a actualizar
        validated_data: Datos validados para actualizar
        user: Usuario que intenta actualizar

    Returns:
        RoutineExercise actualizado

    Raises:
        NotFound: Si el ejercicio en rutina no existe
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Obtener ejercicio en rutina
    routine_exercise = get_routine_exercise_by_id_repository(
        routine_exercise_id=routine_exercise_id
    )

    if not routine_exercise:
        raise NotFound("Ejercicio en rutina no encontrado")

    # Verificar permisos
    if routine_exercise.block.day.week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede actualizar este ejercicio en rutina")

    # Actualizar ejercicio en rutina
    updated_routine_exercise = update_routine_exercise_repository(
        routine_exercise=routine_exercise, validated_data=validated_data
    )

    return updated_routine_exercise


def delete_routine_exercise_service(routine_exercise_id: int, user: User) -> None:
    """
    Servicio para eliminar un ejercicio en rutina.

    Args:
        routine_exercise_id: ID del ejercicio en rutina a eliminar
        user: Usuario que intenta eliminar

    Raises:
        NotFound: Si el ejercicio en rutina no existe
        PermissionDenied: Si el usuario no es el creador de la rutina
    """
    # Obtener ejercicio en rutina
    routine_exercise = get_routine_exercise_by_id_repository(
        routine_exercise_id=routine_exercise_id
    )

    if not routine_exercise:
        raise NotFound("Ejercicio en rutina no encontrado")

    # Verificar permisos
    if routine_exercise.block.day.week.routine.created_by.id != user.id:
        raise PermissionDenied("Solo el creador puede eliminar este ejercicio en rutina")

    # Eliminar ejercicio en rutina
    delete_routine_exercise_repository(routine_exercise=routine_exercise)


def get_routine_full_service(routine_id: int, user: User) -> Routine:
    """
    Servicio para obtener una rutina completa con toda su jerarquía.

    Args:
        routine_id: ID de la rutina
        user: Usuario autenticado

    Returns:
        Routine con toda su jerarquía

    Raises:
        NotFound: Si la rutina no existe o no pertenece al usuario
    """
    # Obtener rutina completa
    routine = get_routine_full_repository(routine_id=routine_id)

    if not routine:
        raise NotFound("Rutina no encontrada")

    # Verificar permisos (solo el creador puede ver)
    if routine.created_by.id != user.id:
        raise NotFound("Rutina no encontrada")

    return routine
