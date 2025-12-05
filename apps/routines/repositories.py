from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from django.db.models import Prefetch, QuerySet

from apps.routines.models import Block, Day, Routine, RoutineExercise, Week

if TYPE_CHECKING:
    from apps.users.models import User


def list_routines_repository(
    user: Optional[User] = None,
    filters: Optional[dict[str, Any]] = None,
) -> QuerySet[Routine]:
    """
    Lista rutinas con filtros por usuario.

    Args:
        user: Usuario creador (opcional)
        filters: Diccionario con filtros adicionales

    Returns:
        QuerySet de rutinas filtradas
    """
    queryset = Routine.objects.select_related("created_by").all()

    if user:
        queryset = queryset.filter(created_by=user)

    if filters:
        if filters.get("isActive") is not None:
            queryset = queryset.filter(is_active=filters["isActive"])

    queryset = queryset.order_by("-created_at")

    return queryset


def get_routine_by_id_repository(routine_id: int) -> Optional[Routine]:
    """
    Obtiene una rutina por su ID.

    Args:
        routine_id: ID de la rutina

    Returns:
        Routine o None si no existe
    """
    try:
        return Routine.objects.select_related("created_by").get(id=routine_id)
    except Routine.DoesNotExist:
        return None


def create_routine_repository(validated_data: dict[str, Any], user: User) -> Routine:
    """
    Crea una nueva rutina.

    Args:
        validated_data: Datos validados de la rutina
        user: Usuario que crea la rutina

    Returns:
        Routine creada
    """
    routine_data = {
        "name": validated_data.get("name"),
        "description": validated_data.get("description"),
        "duration_weeks": validated_data.get("durationWeeks"),
        "duration_months": validated_data.get("durationMonths"),
        "is_active": validated_data.get("isActive", True),
        "created_by": user,
    }

    # Eliminar None values
    routine_data = {k: v for k, v in routine_data.items() if v is not None}

    return Routine.objects.create(**routine_data)


def update_routine_repository(routine: Routine, validated_data: dict[str, Any]) -> Routine:
    """
    Actualiza una rutina existente.

    Args:
        routine: Instancia de la rutina a actualizar
        validated_data: Datos validados para actualizar

    Returns:
        Routine actualizada
    """
    if "name" in validated_data:
        routine.name = validated_data["name"]
    if "description" in validated_data:
        routine.description = validated_data["description"]
    if "durationWeeks" in validated_data:
        routine.duration_weeks = validated_data["durationWeeks"]
    if "durationMonths" in validated_data:
        routine.duration_months = validated_data["durationMonths"]
    if "isActive" in validated_data:
        routine.is_active = validated_data["isActive"]

    routine.save()
    return routine


def delete_routine_repository(routine: Routine) -> Routine:
    """
    Realiza soft delete de una rutina (marca isActive=False).

    Args:
        routine: Instancia de la rutina a eliminar

    Returns:
        Routine con isActive=False
    """
    routine.is_active = False
    routine.save()
    return routine


# Repositorios para Week
def list_weeks_by_routine_repository(routine_id: int) -> QuerySet[Week]:
    """
    Lista semanas de una rutina ordenadas por weekNumber.

    Args:
        routine_id: ID de la rutina

    Returns:
        QuerySet de semanas
    """
    return Week.objects.filter(routine_id=routine_id).order_by("week_number")


def get_week_by_id_repository(week_id: int) -> Optional[Week]:
    """
    Obtiene una semana por su ID.

    Args:
        week_id: ID de la semana

    Returns:
        Week o None si no existe
    """
    try:
        return Week.objects.select_related("routine").get(id=week_id)
    except Week.DoesNotExist:
        return None


def create_week_repository(routine_id: int, validated_data: dict[str, Any]) -> Week:
    """
    Crea una nueva semana.

    Args:
        routine_id: ID de la rutina
        validated_data: Datos validados de la semana

    Returns:
        Week creada
    """
    week_data = {
        "routine_id": routine_id,
        "week_number": validated_data.get("weekNumber"),
        "notes": validated_data.get("notes"),
    }

    week_data = {k: v for k, v in week_data.items() if v is not None}

    return Week.objects.create(**week_data)


def update_week_repository(week: Week, validated_data: dict[str, Any]) -> Week:
    """
    Actualiza una semana existente.

    Args:
        week: Instancia de la semana a actualizar
        validated_data: Datos validados para actualizar

    Returns:
        Week actualizada
    """
    if "weekNumber" in validated_data:
        week.week_number = validated_data["weekNumber"]
    if "notes" in validated_data:
        week.notes = validated_data["notes"]

    week.save()
    return week


def delete_week_repository(week: Week) -> None:
    """
    Elimina una semana (CASCADE eliminará días, bloques y ejercicios).

    Args:
        week: Instancia de la semana a eliminar
    """
    week.delete()


# Repositorios para Day
def list_days_by_week_repository(week_id: int) -> QuerySet[Day]:
    """
    Lista días de una semana ordenados por dayNumber.

    Args:
        week_id: ID de la semana

    Returns:
        QuerySet de días
    """
    return Day.objects.filter(week_id=week_id).order_by("day_number")


def get_day_by_id_repository(day_id: int) -> Optional[Day]:
    """
    Obtiene un día por su ID.

    Args:
        day_id: ID del día

    Returns:
        Day o None si no existe
    """
    try:
        return Day.objects.select_related("week", "week__routine").get(id=day_id)
    except Day.DoesNotExist:
        return None


def create_day_repository(week_id: int, validated_data: dict[str, Any]) -> Day:
    """
    Crea un nuevo día.

    Args:
        week_id: ID de la semana
        validated_data: Datos validados del día

    Returns:
        Day creado
    """
    day_data = {
        "week_id": week_id,
        "day_number": validated_data.get("dayNumber"),
        "name": validated_data.get("name"),
        "notes": validated_data.get("notes"),
    }

    day_data = {k: v for k, v in day_data.items() if v is not None}

    return Day.objects.create(**day_data)


def update_day_repository(day: Day, validated_data: dict[str, Any]) -> Day:
    """
    Actualiza un día existente.

    Args:
        day: Instancia del día a actualizar
        validated_data: Datos validados para actualizar

    Returns:
        Day actualizado
    """
    if "dayNumber" in validated_data:
        day.day_number = validated_data["dayNumber"]
    if "name" in validated_data:
        day.name = validated_data["name"]
    if "notes" in validated_data:
        day.notes = validated_data["notes"]

    day.save()
    return day


def delete_day_repository(day: Day) -> None:
    """
    Elimina un día (CASCADE eliminará bloques y ejercicios).

    Args:
        day: Instancia del día a eliminar
    """
    day.delete()


# Repositorios para Block
def list_blocks_by_day_repository(day_id: int) -> QuerySet[Block]:
    """
    Lista bloques de un día ordenados por order.

    Args:
        day_id: ID del día

    Returns:
        QuerySet de bloques
    """
    return Block.objects.filter(day_id=day_id).order_by("order", "id")


def get_block_by_id_repository(block_id: int) -> Optional[Block]:
    """
    Obtiene un bloque por su ID.

    Args:
        block_id: ID del bloque

    Returns:
        Block o None si no existe
    """
    try:
        return Block.objects.select_related("day", "day__week", "day__week__routine").get(
            id=block_id
        )
    except Block.DoesNotExist:
        return None


def create_block_repository(day_id: int, validated_data: dict[str, Any]) -> Block:
    """
    Crea un nuevo bloque.

    Args:
        day_id: ID del día
        validated_data: Datos validados del bloque

    Returns:
        Block creado
    """
    block_data = {
        "day_id": day_id,
        "name": validated_data.get("name"),
        "order": validated_data.get("order"),
        "notes": validated_data.get("notes"),
    }

    block_data = {k: v for k, v in block_data.items() if v is not None}

    return Block.objects.create(**block_data)


def update_block_repository(block: Block, validated_data: dict[str, Any]) -> Block:
    """
    Actualiza un bloque existente.

    Args:
        block: Instancia del bloque a actualizar
        validated_data: Datos validados para actualizar

    Returns:
        Block actualizado
    """
    if "name" in validated_data:
        block.name = validated_data["name"]
    if "order" in validated_data:
        block.order = validated_data["order"]
    if "notes" in validated_data:
        block.notes = validated_data["notes"]

    block.save()
    return block


def delete_block_repository(block: Block) -> None:
    """
    Elimina un bloque (CASCADE eliminará ejercicios).

    Args:
        block: Instancia del bloque a eliminar
    """
    block.delete()


# Repositorios para RoutineExercise
def list_routine_exercises_by_block_repository(
    block_id: int,
) -> QuerySet[RoutineExercise]:
    """
    Lista ejercicios de un bloque ordenados por order.

    Args:
        block_id: ID del bloque

    Returns:
        QuerySet de ejercicios en rutina
    """
    return (
        RoutineExercise.objects.filter(block_id=block_id)
        .select_related("exercise")
        .order_by("order", "id")
    )


def get_routine_exercise_by_id_repository(
    routine_exercise_id: int,
) -> Optional[RoutineExercise]:
    """
    Obtiene un ejercicio en rutina por su ID.

    Args:
        routine_exercise_id: ID del ejercicio en rutina

    Returns:
        RoutineExercise o None si no existe
    """
    try:
        return RoutineExercise.objects.select_related(
            "exercise", "block", "block__day", "block__day__week", "block__day__week__routine"
        ).get(id=routine_exercise_id)
    except RoutineExercise.DoesNotExist:
        return None


def create_routine_exercise_repository(
    block_id: int, exercise_id: int, validated_data: dict[str, Any]
) -> RoutineExercise:
    """
    Crea un nuevo ejercicio en rutina.

    Args:
        block_id: ID del bloque
        exercise_id: ID del ejercicio de la biblioteca
        validated_data: Datos validados del ejercicio en rutina

    Returns:
        RoutineExercise creado
    """
    routine_exercise_data = {
        "block_id": block_id,
        "exercise_id": exercise_id,
        "order": validated_data.get("order"),
        "sets": validated_data.get("sets"),
        "repetitions": validated_data.get("repetitions"),
        "weight": validated_data.get("weight"),
        "weight_percentage": validated_data.get("weightPercentage"),
        "tempo": validated_data.get("tempo"),
        "rest_seconds": validated_data.get("restSeconds"),
        "notes": validated_data.get("notes"),
    }

    routine_exercise_data = {k: v for k, v in routine_exercise_data.items() if v is not None}

    return RoutineExercise.objects.create(**routine_exercise_data)


def update_routine_exercise_repository(
    routine_exercise: RoutineExercise, validated_data: dict[str, Any]
) -> RoutineExercise:
    """
    Actualiza un ejercicio en rutina existente.

    Args:
        routine_exercise: Instancia del ejercicio en rutina a actualizar
        validated_data: Datos validados para actualizar

    Returns:
        RoutineExercise actualizado
    """
    if "order" in validated_data:
        routine_exercise.order = validated_data["order"]
    if "sets" in validated_data:
        routine_exercise.sets = validated_data["sets"]
    if "repetitions" in validated_data:
        routine_exercise.repetitions = validated_data["repetitions"]
    if "weight" in validated_data:
        routine_exercise.weight = validated_data["weight"]
    if "weightPercentage" in validated_data:
        routine_exercise.weight_percentage = validated_data["weightPercentage"]
    if "tempo" in validated_data:
        routine_exercise.tempo = validated_data["tempo"]
    if "restSeconds" in validated_data:
        routine_exercise.rest_seconds = validated_data["restSeconds"]
    if "notes" in validated_data:
        routine_exercise.notes = validated_data["notes"]

    routine_exercise.save()
    return routine_exercise


def delete_routine_exercise_repository(routine_exercise: RoutineExercise) -> None:
    """
    Elimina un ejercicio en rutina.

    Args:
        routine_exercise: Instancia del ejercicio en rutina a eliminar
    """
    routine_exercise.delete()


def get_routine_full_repository(routine_id: int) -> Optional[Routine]:
    """
    Obtiene una rutina completa con toda su jerarquía optimizada.

    Args:
        routine_id: ID de la rutina

    Returns:
        Routine con toda su jerarquía o None si no existe
    """
    try:
        return (
            Routine.objects.select_related("created_by")
            .prefetch_related(
                Prefetch(
                    "weeks",
                    queryset=Week.objects.order_by("week_number").prefetch_related(
                        Prefetch(
                            "days",
                            queryset=Day.objects.order_by("day_number").prefetch_related(
                                Prefetch(
                                    "blocks",
                                    queryset=Block.objects.order_by("order", "id").prefetch_related(
                                        Prefetch(
                                            "routine_exercises",
                                            queryset=RoutineExercise.objects.order_by(
                                                "order", "id"
                                            ).select_related("exercise"),
                                        )
                                    ),
                                )
                            ),
                        )
                    ),
                )
            )
            .get(id=routine_id)
        )
    except Routine.DoesNotExist:
        return None
