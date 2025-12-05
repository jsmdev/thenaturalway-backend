from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models import Prefetch, QuerySet

from apps.sessions.models import Session, SessionExercise

if TYPE_CHECKING:
    from datetime import date

    from apps.users.models import User


def list_sessions_repository(
    user: User,
    routine_id: int | None = None,
    date_filter: date | None = None,
) -> QuerySet[Session]:
    """
    Lista sesiones con filtros por usuario, rutina y fecha.

    Args:
        user: Usuario propietario de las sesiones (requerido)
        routine_id: ID de rutina para filtrar (opcional)
        date_filter: Fecha para filtrar (opcional)

    Returns:
        QuerySet de sesiones filtradas, ordenadas por fecha descendente
    """
    queryset = Session.objects.select_related("user", "routine").filter(user=user)

    # Aplicar filtros
    if routine_id:
        queryset = queryset.filter(routine_id=routine_id)
    if date_filter:
        queryset = queryset.filter(date=date_filter)

    # Ordenar por fecha descendente (más recientes primero)
    queryset = queryset.order_by("-date", "-created_at")

    return queryset


def get_session_by_id_repository(session_id: int) -> Session | None:
    """
    Obtiene una sesión por su ID.

    Args:
        session_id: ID de la sesión

    Returns:
        Session o None si no existe
    """
    try:
        return Session.objects.select_related("user", "routine").get(id=session_id)
    except Session.DoesNotExist:
        return None


def get_session_full_repository(session_id: int) -> Session | None:
    """
    Obtiene una sesión por su ID con ejercicios precargados.

    Args:
        session_id: ID de la sesión

    Returns:
        Session con ejercicios precargados o None si no existe
    """
    try:
        return (
            Session.objects.select_related("user", "routine")
            .prefetch_related(
                Prefetch(
                    "session_exercises",
                    queryset=SessionExercise.objects.select_related("exercise").order_by(
                        "order", "id"
                    ),
                    to_attr="prefetched_session_exercises",
                )
            )
            .get(id=session_id)
        )
    except Session.DoesNotExist:
        return None


def create_session_repository(validated_data: dict[str, Any], user: User) -> Session:
    """
    Crea una nueva sesión.

    Args:
        validated_data: Datos validados de la sesión
        user: Usuario que crea la sesión

    Returns:
        Session creada
    """
    # Mapear nombres de dominio a nombres de modelo
    session_data = {
        "user": user,
        "routine_id": validated_data.get("routineId"),
        "date": validated_data.get("date"),
        "start_time": validated_data.get("startTime"),
        "end_time": validated_data.get("endTime"),
        "duration_minutes": validated_data.get("durationMinutes"),
        "notes": validated_data.get("notes"),
        "rpe": validated_data.get("rpe"),
        "energy_level": validated_data.get("energyLevel"),
        "sleep_hours": validated_data.get("sleepHours"),
    }

    # Eliminar None values excepto para campos que pueden ser None intencionalmente
    session_data = {
        k: v
        for k, v in session_data.items()
        if v is not None
        or k
        in [
            "routine_id",
            "notes",
            "start_time",
            "end_time",
            "duration_minutes",
            "rpe",
            "energy_level",
            "sleep_hours",
        ]
    }

    return Session.objects.create(**session_data)


def update_session_repository(session: Session, validated_data: dict[str, Any]) -> Session:
    """
    Actualiza una sesión existente.

    Args:
        session: Instancia de la sesión a actualizar
        validated_data: Datos validados para actualizar

    Returns:
        Session actualizada
    """
    # Mapear nombres de dominio a nombres de modelo
    if "routineId" in validated_data:
        session.routine_id = validated_data["routineId"]
    if "date" in validated_data:
        session.date = validated_data["date"]
    if "startTime" in validated_data:
        session.start_time = validated_data["startTime"]
    if "endTime" in validated_data:
        session.end_time = validated_data["endTime"]
    if "durationMinutes" in validated_data:
        session.duration_minutes = validated_data["durationMinutes"]
    if "notes" in validated_data:
        session.notes = validated_data["notes"]
    if "rpe" in validated_data:
        session.rpe = validated_data["rpe"]
    if "energyLevel" in validated_data:
        session.energy_level = validated_data["energyLevel"]
    if "sleepHours" in validated_data:
        session.sleep_hours = validated_data["sleepHours"]

    session.save()
    return session


def delete_session_repository(session: Session) -> None:
    """
    Elimina una sesión físicamente.

    Args:
        session: Instancia de la sesión a eliminar
    """
    session.delete()


def list_session_exercises_repository(
    session: Session, ordering: str | None = None
) -> QuerySet[SessionExercise]:
    """
    Lista ejercicios de una sesión ordenados por order.

    Args:
        session: Sesión de la que obtener ejercicios
        ordering: Campo para ordenamiento (opcional, por defecto "order", "id")

    Returns:
        QuerySet de ejercicios de la sesión ordenados
    """
    queryset = SessionExercise.objects.select_related("exercise").filter(session=session)
    queryset = queryset.order_by(ordering) if ordering else queryset.order_by("order", "id")
    return queryset


def get_session_exercise_by_id_repository(session_exercise_id: int) -> SessionExercise | None:
    """
    Obtiene un ejercicio de sesión por su ID.

    Args:
        session_exercise_id: ID del ejercicio de sesión

    Returns:
        SessionExercise o None si no existe
    """
    try:
        return SessionExercise.objects.select_related("session", "exercise").get(
            id=session_exercise_id
        )
    except SessionExercise.DoesNotExist:
        return None


def create_session_exercise_repository(
    session: Session, validated_data: dict[str, Any]
) -> SessionExercise:
    """
    Crea un nuevo ejercicio en una sesión.

    Args:
        session: Sesión a la que añadir el ejercicio
        validated_data: Datos validados del ejercicio

    Returns:
        SessionExercise creado
    """
    exercise_data = {
        "session": session,
        "exercise_id": validated_data.get("exerciseId"),
        "order": validated_data.get("order"),
        "sets_completed": validated_data.get("setsCompleted"),
        "repetitions": validated_data.get("repetitions"),
        "weight": validated_data.get("weight"),
        "rpe": validated_data.get("rpe"),
        "rest_seconds": validated_data.get("restSeconds"),
        "notes": validated_data.get("notes"),
    }

    # Eliminar None values excepto para campos opcionales
    exercise_data = {
        k: v
        for k, v in exercise_data.items()
        if v is not None
        or k in ["order", "sets_completed", "repetitions", "weight", "rpe", "rest_seconds", "notes"]
    }

    return SessionExercise.objects.create(**exercise_data)


def update_session_exercise_repository(
    session_exercise: SessionExercise, validated_data: dict[str, Any]
) -> SessionExercise:
    """
    Actualiza un ejercicio de sesión existente.

    Args:
        session_exercise: Instancia del ejercicio a actualizar
        validated_data: Datos validados para actualizar

    Returns:
        SessionExercise actualizado
    """
    if "exerciseId" in validated_data:
        session_exercise.exercise_id = validated_data["exerciseId"]
    if "order" in validated_data:
        session_exercise.order = validated_data["order"]
    if "setsCompleted" in validated_data:
        session_exercise.sets_completed = validated_data["setsCompleted"]
    if "repetitions" in validated_data:
        session_exercise.repetitions = validated_data["repetitions"]
    if "weight" in validated_data:
        session_exercise.weight = validated_data["weight"]
    if "rpe" in validated_data:
        session_exercise.rpe = validated_data["rpe"]
    if "restSeconds" in validated_data:
        session_exercise.rest_seconds = validated_data["restSeconds"]
    if "notes" in validated_data:
        session_exercise.notes = validated_data["notes"]

    session_exercise.save()
    return session_exercise


def delete_session_exercise_repository(session_exercise: SessionExercise) -> None:
    """
    Elimina un ejercicio de sesión físicamente.

    Args:
        session_exercise: Instancia del ejercicio a eliminar
    """
    session_exercise.delete()
