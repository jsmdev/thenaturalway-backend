from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Any, List, TypedDict
from datetime import date, datetime

from django.db.models import Prefetch
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied

from apps.sessions.repositories import (
    list_sessions_repository,
    get_session_by_id_repository,
    create_session_repository,
    update_session_repository,
    delete_session_repository,
    list_session_exercises_repository,
    get_session_exercise_by_id_repository,
    create_session_exercise_repository,
    update_session_exercise_repository,
    delete_session_exercise_repository,
)
from apps.sessions.models import Session, SessionExercise

if TYPE_CHECKING:
    from apps.users.models import User


class SessionCreateData(TypedDict, total=False):
    """Estructura de datos para crear una sesión."""
    date: date
    routineId: Optional[int]
    startTime: Optional[datetime]
    endTime: Optional[datetime]
    durationMinutes: Optional[int]
    notes: Optional[str]
    rpe: Optional[int]
    energyLevel: Optional[str]
    sleepHours: Optional[float]


class SessionUpdateData(TypedDict, total=False):
    """Estructura de datos para actualizar una sesión."""
    date: date
    routineId: Optional[int]
    startTime: Optional[datetime]
    endTime: Optional[datetime]
    durationMinutes: Optional[int]
    notes: Optional[str]
    rpe: Optional[int]
    energyLevel: Optional[str]
    sleepHours: Optional[float]


class SessionExerciseCreateData(TypedDict, total=False):
    """Estructura de datos para crear un ejercicio de sesión."""
    exerciseId: int
    order: Optional[int]
    setsCompleted: Optional[int]
    repetitions: Optional[str]
    weight: Optional[float]
    rpe: Optional[int]
    restSeconds: Optional[int]
    notes: Optional[str]


class SessionExerciseUpdateData(TypedDict, total=False):
    """Estructura de datos para actualizar un ejercicio de sesión."""
    exerciseId: Optional[int]
    order: Optional[int]
    setsCompleted: Optional[int]
    repetitions: Optional[str]
    weight: Optional[float]
    rpe: Optional[int]
    restSeconds: Optional[int]
    notes: Optional[str]


def list_sessions_service(
    user: "User",
    routine_id: Optional[int] = None,
    date_filter: Optional[date] = None,
) -> List["Session"]:
    """
    Servicio para listar sesiones del usuario con filtros.

    Args:
        user: Usuario propietario de las sesiones (requerido)
        routine_id: ID de rutina para filtrar (opcional)
        date_filter: Fecha para filtrar (opcional)

    Returns:
        Lista de sesiones del usuario
        
    Raises:
        ValidationError: Si la rutina no existe o no pertenece al usuario
    """
    # Validar que si se proporciona routine_id, la rutina existe y pertenece al usuario
    if routine_id is not None:
        from apps.routines.repositories import get_routine_by_id_repository
        routine = get_routine_by_id_repository(routine_id=routine_id)
        if not routine:
            raise ValidationError({"routineId": "Rutina no encontrada"})
        if routine.created_by.id != user.id:
            raise ValidationError(
                {"routineId": "Solo puedes listar sesiones de tus propias rutinas"}
            )
    
    queryset = list_sessions_repository(
        user=user, routine_id=routine_id, date_filter=date_filter
    )
    return list(queryset)


def get_session_service(session_id: int, user: "User") -> "Session":
    """
    Servicio para obtener una sesión por ID.

    Args:
        session_id: ID de la sesión
        user: Usuario que solicita la sesión

    Returns:
        Session

    Raises:
        NotFound: Si la sesión no existe
        PermissionDenied: Si el usuario no es el propietario
    """
    session = get_session_by_id_repository(session_id=session_id)

    if not session:
        raise NotFound("Sesión no encontrada")

    # Verificar permisos (solo el propietario puede ver)
    if session.user.id != user.id:
        raise PermissionDenied("Solo puedes ver tus propias sesiones")

    return session


def create_session_service(
    validated_data: SessionCreateData, user: "User"
) -> "Session":
    """
    Servicio para crear una nueva sesión.

    Args:
        validated_data: Datos validados de la sesión
        user: Usuario que crea la sesión

    Returns:
        Session creada

    Raises:
        ValidationError: Si los datos no son válidos
    """
    # Validar que date esté presente
    if not validated_data.get("date"):
        raise ValidationError({"date": "La fecha es requerida"})

    # Validación temprana de energyLevel (también validado en el modelo)
    if "energyLevel" in validated_data and validated_data["energyLevel"]:
        valid_energy_levels = [choice[0] for choice in Session.ENERGY_LEVEL_CHOICES]
        if validated_data["energyLevel"] not in valid_energy_levels:
            raise ValidationError(
                {
                    "energyLevel": f"Debe ser uno de: {', '.join(valid_energy_levels)}"
                }
            )

    # Validar que si se proporciona routineId, la rutina pertenezca al usuario
    if "routineId" in validated_data and validated_data["routineId"]:
        from apps.routines.repositories import get_routine_by_id_repository
        routine = get_routine_by_id_repository(routine_id=validated_data["routineId"])
        if not routine:
            raise ValidationError({"routineId": "Rutina no encontrada"})
        if routine.created_by.id != user.id:
            raise ValidationError(
                {"routineId": "Solo puedes vincular sesiones a tus propias rutinas"}
            )

    # Calcular duración automáticamente si se proporcionan startTime y endTime
    if validated_data.get("startTime") and validated_data.get("endTime"):
        start_time = validated_data["startTime"]
        end_time = validated_data["endTime"]
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        if end_time <= start_time:
            raise ValidationError(
                {"endTime": "La hora de finalización debe ser posterior a la hora de inicio"}
            )
        delta = end_time - start_time
        validated_data["durationMinutes"] = int(delta.total_seconds() / 60)

    # Crear sesión
    session = create_session_repository(validated_data=validated_data, user=user)

    return session


def update_session_service(
    session_id: int, validated_data: SessionUpdateData, user: "User"
) -> "Session":
    """
    Servicio para actualizar una sesión existente.

    Args:
        session_id: ID de la sesión a actualizar
        validated_data: Datos validados para actualizar
        user: Usuario que intenta actualizar

    Returns:
        Session actualizada

    Raises:
        NotFound: Si la sesión no existe
        PermissionDenied: Si el usuario no es el propietario
        ValidationError: Si los datos no son válidos
    """
    # Obtener sesión
    session = get_session_by_id_repository(session_id=session_id)

    if not session:
        raise NotFound("Sesión no encontrada")

    # Verificar permisos (solo el propietario puede actualizar)
    if session.user.id != user.id:
        raise PermissionDenied("Solo puedes actualizar tus propias sesiones")

    # Validar routineId si se proporciona
    if "routineId" in validated_data and validated_data["routineId"]:
        from apps.routines.repositories import get_routine_by_id_repository
        routine = get_routine_by_id_repository(routine_id=validated_data["routineId"])
        if not routine:
            raise ValidationError({"routineId": "Rutina no encontrada"})
        if routine.created_by.id != user.id:
            raise ValidationError(
                {"routineId": "Solo puedes vincular sesiones a tus propias rutinas"}
            )

    # Calcular duración automáticamente si se proporcionan startTime y endTime
    if validated_data.get("startTime") and validated_data.get("endTime"):
        start_time = validated_data["startTime"]
        end_time = validated_data["endTime"]
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        if end_time <= start_time:
            raise ValidationError(
                {"endTime": "La hora de finalización debe ser posterior a la hora de inicio"}
            )
        delta = end_time - start_time
        validated_data["durationMinutes"] = int(delta.total_seconds() / 60)

    # Actualizar sesión
    updated_session = update_session_repository(
        session=session, validated_data=validated_data
    )

    return updated_session


def delete_session_service(session_id: int, user: "User") -> None:
    """
    Servicio para eliminar una sesión.

    Args:
        session_id: ID de la sesión a eliminar
        user: Usuario que intenta eliminar

    Raises:
        NotFound: Si la sesión no existe
        PermissionDenied: Si el usuario no es el propietario
    """
    # Obtener sesión
    session = get_session_by_id_repository(session_id=session_id)

    if not session:
        raise NotFound("Sesión no encontrada")

    # Verificar permisos (solo el propietario puede eliminar)
    if session.user.id != user.id:
        raise PermissionDenied("Solo puedes eliminar tus propias sesiones")

    # Eliminar sesión
    delete_session_repository(session=session)


def get_session_full_service(session_id: int, user: "User") -> "Session":
    """
    Servicio para obtener una sesión completa con ejercicios asociados.

    Args:
        session_id: ID de la sesión
        user: Usuario que solicita la sesión

    Returns:
        Session con ejercicios precargados

    Raises:
        NotFound: Si la sesión no existe
        PermissionDenied: Si el usuario no es el propietario
    """
    session = get_session_by_id_repository(session_id=session_id)

    if not session:
        raise NotFound("Sesión no encontrada")

    # Verificar permisos
    if session.user.id != user.id:
        raise PermissionDenied("Solo puedes ver tus propias sesiones")

    # Precargar ejercicios con optimización usando prefetch_related
    from apps.sessions.repositories import get_session_full_repository
    session = get_session_full_repository(session_id=session_id)

    if not session:
        raise NotFound("Sesión no encontrada")

    return session


def list_session_exercises_service(
    session_id: int, user: "User"
) -> List["SessionExercise"]:
    """
    Servicio para listar ejercicios de una sesión.

    Args:
        session_id: ID de la sesión
        user: Usuario que solicita los ejercicios

    Returns:
        Lista de ejercicios de la sesión

    Raises:
        NotFound: Si la sesión no existe
        PermissionDenied: Si el usuario no es el propietario de la sesión
    """
    # Verificar que la sesión existe y pertenece al usuario
    session = get_session_service(session_id=session_id, user=user)

    # Obtener ejercicios
    queryset = list_session_exercises_repository(session=session)
    return list(queryset)


def get_session_exercise_service(
    session_exercise_id: int, user: "User"
) -> "SessionExercise":
    """
    Servicio para obtener un ejercicio de sesión por ID.

    Args:
        session_exercise_id: ID del ejercicio de sesión
        user: Usuario que solicita el ejercicio

    Returns:
        SessionExercise

    Raises:
        NotFound: Si el ejercicio no existe
        PermissionDenied: Si el usuario no es el propietario de la sesión
    """
    session_exercise = get_session_exercise_by_id_repository(
        session_exercise_id=session_exercise_id
    )

    if not session_exercise:
        raise NotFound("Ejercicio de sesión no encontrado")

    # Verificar permisos (solo el propietario de la sesión puede ver)
    if session_exercise.session.user.id != user.id:
        raise PermissionDenied("Solo puedes ver ejercicios de tus propias sesiones")

    return session_exercise


def create_session_exercise_service(
    session_id: int, validated_data: SessionExerciseCreateData, user: "User"
) -> "SessionExercise":
    """
    Servicio para crear un nuevo ejercicio en una sesión.

    Args:
        session_id: ID de la sesión
        validated_data: Datos validados del ejercicio
        user: Usuario que crea el ejercicio

    Returns:
        SessionExercise creado

    Raises:
        NotFound: Si la sesión o el ejercicio no existen
        PermissionDenied: Si el usuario no es el propietario de la sesión
        ValidationError: Si los datos no son válidos
    """
    # Verificar que la sesión existe y pertenece al usuario
    session = get_session_service(session_id=session_id, user=user)

    # Validar que exerciseId esté presente
    if not validated_data.get("exerciseId"):
        raise ValidationError({"exerciseId": "El ejercicio es requerido"})

    # Validar que el ejercicio existe
    from apps.exercises.repositories import get_exercise_by_id_repository
    exercise = get_exercise_by_id_repository(
        exercise_id=validated_data["exerciseId"]
    )
    if not exercise:
        raise ValidationError({"exerciseId": "Ejercicio no encontrado"})

    # Crear ejercicio en sesión
    session_exercise = create_session_exercise_repository(
        session=session, validated_data=validated_data
    )

    return session_exercise


def update_session_exercise_service(
    session_exercise_id: int, validated_data: SessionExerciseUpdateData, user: "User"
) -> "SessionExercise":
    """
    Servicio para actualizar un ejercicio de sesión existente.

    Args:
        session_exercise_id: ID del ejercicio a actualizar
        validated_data: Datos validados para actualizar
        user: Usuario que intenta actualizar

    Returns:
        SessionExercise actualizado

    Raises:
        NotFound: Si el ejercicio no existe
        PermissionDenied: Si el usuario no es el propietario de la sesión
        ValidationError: Si los datos no son válidos
    """
    # Obtener ejercicio
    session_exercise = get_session_exercise_by_id_repository(
        session_exercise_id=session_exercise_id
    )
    if not session_exercise:
        raise NotFound("Ejercicio de sesión no encontrado")
    
    # Verificar permisos
    if session_exercise.session.user.id != user.id:
        raise PermissionDenied("Solo puedes actualizar ejercicios en tus propias sesiones")

    # Validar exerciseId si se proporciona
    if "exerciseId" in validated_data and validated_data["exerciseId"]:
        from apps.exercises.repositories import get_exercise_by_id_repository
        exercise = get_exercise_by_id_repository(
            exercise_id=validated_data["exerciseId"]
        )
        if not exercise:
            raise ValidationError({"exerciseId": "Ejercicio no encontrado"})

    # Actualizar ejercicio
    updated_exercise = update_session_exercise_repository(
        session_exercise=session_exercise, validated_data=validated_data
    )

    return updated_exercise


def delete_session_exercise_service(
    session_exercise_id: int, user: "User"
) -> None:
    """
    Servicio para eliminar un ejercicio de sesión.

    Args:
        session_exercise_id: ID del ejercicio a eliminar
        user: Usuario que intenta eliminar

    Raises:
        NotFound: Si el ejercicio no existe
        PermissionDenied: Si el usuario no es el propietario de la sesión
    """
    # Obtener ejercicio (esto también verifica permisos)
    session_exercise = get_session_exercise_service(
        session_exercise_id=session_exercise_id, user=user
    )

    # Eliminar ejercicio
    delete_session_exercise_repository(session_exercise=session_exercise)

