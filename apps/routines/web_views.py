from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator

from apps.routines.forms import (
    RoutineCreateForm,
    RoutineUpdateForm,
    WeekForm,
    DayForm,
    BlockForm,
    RoutineExerciseForm,
)
from apps.routines.services import (
    list_routines_service,
    get_routine_service,
    get_routine_full_service,
    create_routine_service,
    update_routine_service,
    delete_routine_service,
    create_week_service,
    create_day_service,
    create_block_service,
    create_routine_exercise_service,
)
from apps.routines.serializers import RoutineSerializer, RoutineFullSerializer
from rest_framework.exceptions import NotFound, PermissionDenied

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


class RoutineListView(View):
    """Vista para listar rutinas del usuario."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra la lista de rutinas del usuario."""
        try:
            routines = list_routines_service(user=request.user)
            serializer = RoutineSerializer(routines, many=True)
            routines_data = serializer.data

            context = {"routines": routines_data}

            return render(request, "routines/list.html", context)

        except Exception as error:
            messages.error(request, f"Error al cargar rutinas: {str(error)}")
            return render(request, "routines/list.html", {"routines": []})


class RoutineDetailView(View):
    """Vista para ver el detalle de una rutina completa con jerarquía."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Muestra el detalle de una rutina con toda su jerarquía."""
        try:
            routine = get_routine_full_service(routine_id=pk, user=request.user)
            serializer = RoutineFullSerializer(routine)
            routine_data = serializer.data

            # Verificar si el usuario es el creador
            is_owner = routine.created_by.id == request.user.id

            context = {
                "routine": routine_data,
                "is_owner": is_owner,
            }

            return render(request, "routines/detail.html", context)

        except NotFound:
            messages.error(request, "Rutina no encontrada.")
            return redirect("routines:list")
        except Exception as error:
            messages.error(request, f"Error al cargar rutina: {str(error)}")
            return redirect("routines:list")


class RoutineCreateView(View):
    """Vista para crear una nueva rutina."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra el formulario de creación."""
        form = RoutineCreateForm()
        return render(request, "routines/form.html", {"form": form, "action": "create"})

    @method_decorator(login_required)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Procesa el formulario de creación."""
        form = RoutineCreateForm(request.POST)

        if not form.is_valid():
            return render(request, "routines/form.html", {"form": form, "action": "create"})

        try:
            validated_data = {
                "name": form.cleaned_data["name"],
                "description": form.cleaned_data.get("description") or None,
                "durationWeeks": form.cleaned_data.get("duration_weeks"),
                "durationMonths": form.cleaned_data.get("duration_months"),
                "isActive": form.cleaned_data.get("is_active", True),
            }

            routine = create_routine_service(validated_data=validated_data, user=request.user)

            messages.success(request, f"Rutina '{routine.name}' creada correctamente.")
            return redirect("routines:detail", pk=routine.id)

        except Exception as error:
            messages.error(request, f"Error al crear rutina: {str(error)}")
            return render(request, "routines/form.html", {"form": form, "action": "create"})


class RoutineUpdateView(View):
    """Vista para actualizar una rutina existente."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Muestra el formulario de actualización."""
        try:
            routine = get_routine_service(routine_id=pk, user=request.user)
            serializer = RoutineSerializer(routine)
            routine_data = serializer.data

            form = RoutineUpdateForm(
                initial={
                    "name": routine_data.get("name"),
                    "description": routine_data.get("description"),
                    "duration_weeks": routine_data.get("durationWeeks"),
                    "duration_months": routine_data.get("durationMonths"),
                    "is_active": routine_data.get("isActive"),
                }
            )

            context = {
                "form": form,
                "routine": routine_data,
                "action": "update",
            }

            return render(request, "routines/form.html", context)

        except NotFound:
            messages.error(request, "Rutina no encontrada.")
            return redirect("routines:list")
        except Exception as error:
            messages.error(request, f"Error al cargar rutina: {str(error)}")
            return redirect("routines:list")

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Procesa el formulario de actualización."""
        form = RoutineUpdateForm(request.POST)

        if not form.is_valid():
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                serializer = RoutineSerializer(routine)
                routine_data = serializer.data
            except Exception:
                routine_data = {}
            return render(
                request, "routines/form.html", {"form": form, "routine": routine_data, "action": "update"}
            )

        try:
            validated_data = {}
            if form.cleaned_data.get("name"):
                validated_data["name"] = form.cleaned_data["name"]
            if form.cleaned_data.get("description") is not None:
                validated_data["description"] = form.cleaned_data["description"] or None
            if form.cleaned_data.get("duration_weeks") is not None:
                validated_data["durationWeeks"] = form.cleaned_data["duration_weeks"]
            if form.cleaned_data.get("duration_months") is not None:
                validated_data["durationMonths"] = form.cleaned_data["duration_months"]
            if "is_active" in form.cleaned_data:
                validated_data["isActive"] = form.cleaned_data["is_active"]

            updated_routine = update_routine_service(
                routine_id=pk, validated_data=validated_data, user=request.user
            )

            messages.success(request, f"Rutina '{updated_routine.name}' actualizada correctamente.")
            return redirect("routines:detail", pk=pk)

        except NotFound:
            messages.error(request, "Rutina no encontrada.")
            return redirect("routines:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para editar esta rutina.")
            return redirect("routines:list")
        except Exception as error:
            messages.error(request, f"Error al actualizar rutina: {str(error)}")
            return redirect("routines:detail", pk=pk)


class RoutineDeleteView(View):
    """Vista para eliminar una rutina (soft delete)."""

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Elimina una rutina."""
        try:
            routine = get_routine_service(routine_id=pk, user=request.user)
            delete_routine_service(routine_id=pk, user=request.user)

            messages.success(request, f"Rutina '{routine.name}' eliminada correctamente.")
            return redirect("routines:list")

        except NotFound:
            messages.error(request, "Rutina no encontrada.")
            return redirect("routines:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para eliminar esta rutina.")
            return redirect("routines:list")
        except Exception as error:
            messages.error(request, f"Error al eliminar rutina: {str(error)}")
            return redirect("routines:detail", pk=pk)


# Vistas web anidadas
class WeekCreateView(View):
    """Vista para crear una semana en una rutina."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Muestra el formulario de creación de semana."""
        try:
            routine = get_routine_service(routine_id=pk, user=request.user)
            form = WeekForm()
            context = {"form": form, "routine_id": pk, "routine_name": routine.name}
            return render(request, "routines/week_form.html", context)
        except NotFound:
            messages.error(request, "Rutina no encontrada.")
            return redirect("routines:list")
        except Exception as error:
            messages.error(request, f"Error al cargar rutina: {str(error)}")
            return redirect("routines:list")

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Procesa el formulario de creación de semana."""
        form = WeekForm(request.POST)

        if not form.is_valid():
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                context = {"form": form, "routine_id": pk, "routine_name": routine.name}
            except Exception:
                context = {"form": form, "routine_id": pk}
            return render(request, "routines/week_form.html", context)

        try:
            validated_data = {
                "weekNumber": form.cleaned_data["week_number"],
                "notes": form.cleaned_data.get("notes") or None,
            }

            create_week_service(routine_id=pk, validated_data=validated_data, user=request.user)

            messages.success(request, "Semana creada correctamente.")
            return redirect("routines:detail", pk=pk)

        except Exception as error:
            messages.error(request, f"Error al crear semana: {str(error)}")
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                context = {"form": form, "routine_id": pk, "routine_name": routine.name}
            except Exception:
                context = {"form": form, "routine_id": pk}
            return render(request, "routines/week_form.html", context)


class DayCreateView(View):
    """Vista para crear un día en una semana."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int, weekId: int) -> HttpResponse:
        """Muestra el formulario de creación de día."""
        try:
            routine = get_routine_service(routine_id=pk, user=request.user)
            from apps.routines.repositories import get_week_by_id_repository
            week = get_week_by_id_repository(week_id=weekId)
            if not week or week.routine.id != pk:
                raise NotFound("Semana no encontrada")
            form = DayForm()
            context = {
                "form": form,
                "routine_id": pk,
                "week_id": weekId,
                "routine_name": routine.name,
                "week_number": week.week_number,
            }
            return render(request, "routines/day_form.html", context)
        except NotFound:
            messages.error(request, "Rutina o semana no encontrada.")
            return redirect("routines:detail", pk=pk)
        except Exception as error:
            messages.error(request, f"Error al cargar: {str(error)}")
            return redirect("routines:detail", pk=pk)

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int, weekId: int) -> HttpResponse:
        """Procesa el formulario de creación de día."""
        form = DayForm(request.POST)

        if not form.is_valid():
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                from apps.routines.repositories import get_week_by_id_repository
                week = get_week_by_id_repository(week_id=weekId)
                context = {
                    "form": form,
                    "routine_id": pk,
                    "week_id": weekId,
                    "routine_name": routine.name,
                    "week_number": week.week_number if week else None,
                }
            except Exception:
                context = {"form": form, "routine_id": pk, "week_id": weekId}
            return render(request, "routines/day_form.html", context)

        try:
            validated_data = {
                "dayNumber": form.cleaned_data["day_number"],
                "name": form.cleaned_data.get("name") or None,
                "notes": form.cleaned_data.get("notes") or None,
            }

            create_day_service(week_id=weekId, validated_data=validated_data, user=request.user)

            messages.success(request, "Día creado correctamente.")
            return redirect("routines:detail", pk=pk)

        except Exception as error:
            messages.error(request, f"Error al crear día: {str(error)}")
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                from apps.routines.repositories import get_week_by_id_repository
                week = get_week_by_id_repository(week_id=weekId)
                context = {
                    "form": form,
                    "routine_id": pk,
                    "week_id": weekId,
                    "routine_name": routine.name,
                    "week_number": week.week_number if week else None,
                }
            except Exception:
                context = {"form": form, "routine_id": pk, "week_id": weekId}
            return render(request, "routines/day_form.html", context)


class BlockCreateView(View):
    """Vista para crear un bloque en un día."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int, dayId: int) -> HttpResponse:
        """Muestra el formulario de creación de bloque."""
        try:
            routine = get_routine_service(routine_id=pk, user=request.user)
            from apps.routines.repositories import get_day_by_id_repository
            day = get_day_by_id_repository(day_id=dayId)
            if not day or day.week.routine.id != pk:
                raise NotFound("Día no encontrado")
            form = BlockForm()
            context = {
                "form": form,
                "routine_id": pk,
                "day_id": dayId,
                "routine_name": routine.name,
                "day_name": day.name or f"Día {day.day_number}",
            }
            return render(request, "routines/block_form.html", context)
        except NotFound:
            messages.error(request, "Rutina o día no encontrado.")
            return redirect("routines:detail", pk=pk)
        except Exception as error:
            messages.error(request, f"Error al cargar: {str(error)}")
            return redirect("routines:detail", pk=pk)

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int, dayId: int) -> HttpResponse:
        """Procesa el formulario de creación de bloque."""
        form = BlockForm(request.POST)

        if not form.is_valid():
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                from apps.routines.repositories import get_day_by_id_repository
                day = get_day_by_id_repository(day_id=dayId)
                context = {
                    "form": form,
                    "routine_id": pk,
                    "day_id": dayId,
                    "routine_name": routine.name,
                    "day_name": day.name or f"Día {day.day_number}" if day else None,
                }
            except Exception:
                context = {"form": form, "routine_id": pk, "day_id": dayId}
            return render(request, "routines/block_form.html", context)

        try:
            validated_data = {
                "name": form.cleaned_data["name"],
                "order": form.cleaned_data.get("order"),
                "notes": form.cleaned_data.get("notes") or None,
            }

            create_block_service(day_id=dayId, validated_data=validated_data, user=request.user)

            messages.success(request, "Bloque creado correctamente.")
            return redirect("routines:detail", pk=pk)

        except Exception as error:
            messages.error(request, f"Error al crear bloque: {str(error)}")
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                from apps.routines.repositories import get_day_by_id_repository
                day = get_day_by_id_repository(day_id=dayId)
                context = {
                    "form": form,
                    "routine_id": pk,
                    "day_id": dayId,
                    "routine_name": routine.name,
                    "day_name": day.name or f"Día {day.day_number}" if day else None,
                }
            except Exception:
                context = {"form": form, "routine_id": pk, "day_id": dayId}
            return render(request, "routines/block_form.html", context)


class RoutineExerciseCreateView(View):
    """Vista para crear un ejercicio en un bloque."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int, blockId: int) -> HttpResponse:
        """Muestra el formulario de creación de ejercicio en rutina."""
        try:
            routine = get_routine_service(routine_id=pk, user=request.user)
            from apps.routines.repositories import get_block_by_id_repository
            block = get_block_by_id_repository(block_id=blockId)
            if not block or block.day.week.routine.id != pk:
                raise NotFound("Bloque no encontrado")
            form = RoutineExerciseForm()
            context = {
                "form": form,
                "routine_id": pk,
                "block_id": blockId,
                "routine_name": routine.name,
                "block_name": block.name,
            }
            return render(request, "routines/exercise_form.html", context)
        except NotFound:
            messages.error(request, "Rutina o bloque no encontrado.")
            return redirect("routines:detail", pk=pk)
        except Exception as error:
            messages.error(request, f"Error al cargar: {str(error)}")
            return redirect("routines:detail", pk=pk)

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int, blockId: int) -> HttpResponse:
        """Procesa el formulario de creación de ejercicio en rutina."""
        form = RoutineExerciseForm(request.POST)

        if not form.is_valid():
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                from apps.routines.repositories import get_block_by_id_repository
                block = get_block_by_id_repository(block_id=blockId)
                context = {
                    "form": form,
                    "routine_id": pk,
                    "block_id": blockId,
                    "routine_name": routine.name,
                    "block_name": block.name if block else None,
                }
            except Exception:
                context = {"form": form, "routine_id": pk, "block_id": blockId}
            return render(request, "routines/exercise_form.html", context)

        try:
            exercise = form.cleaned_data["exercise"]
            validated_data = {
                "order": form.cleaned_data.get("order"),
                "sets": form.cleaned_data.get("sets"),
                "repetitions": form.cleaned_data.get("repetitions") or None,
                "weight": form.cleaned_data.get("weight"),
                "weightPercentage": form.cleaned_data.get("weight_percentage"),
                "tempo": form.cleaned_data.get("tempo") or None,
                "restSeconds": form.cleaned_data.get("rest_seconds"),
                "notes": form.cleaned_data.get("notes") or None,
            }

            create_routine_exercise_service(
                block_id=blockId,
                exercise_id=exercise.id,
                validated_data=validated_data,
                user=request.user,
            )

            messages.success(request, "Ejercicio añadido a la rutina correctamente.")
            return redirect("routines:detail", pk=pk)

        except Exception as error:
            messages.error(request, f"Error al añadir ejercicio: {str(error)}")
            try:
                routine = get_routine_service(routine_id=pk, user=request.user)
                from apps.routines.repositories import get_block_by_id_repository
                block = get_block_by_id_repository(block_id=blockId)
                context = {
                    "form": form,
                    "routine_id": pk,
                    "block_id": blockId,
                    "routine_name": routine.name,
                    "block_name": block.name if block else None,
                }
            except Exception:
                context = {"form": form, "routine_id": pk, "block_id": blockId}
            return render(request, "routines/exercise_form.html", context)
