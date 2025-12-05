from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.sessions.forms import SessionCreateForm, SessionExerciseForm, SessionUpdateForm
from apps.sessions.serializers import SessionFullSerializer, SessionSerializer
from apps.sessions.services import (
    create_session_exercise_service,
    create_session_service,
    delete_session_exercise_service,
    delete_session_service,
    get_session_exercise_service,
    get_session_full_service,
    list_sessions_service,
    update_session_exercise_service,
    update_session_service,
)

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


class SessionListView(View):
    """Vista para listar sesiones del usuario."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra la lista de sesiones del usuario con filtros."""
        # Extraer filtros de query params
        routine_id = None
        if request.GET.get("routineId"):
            try:
                routine_id = int(request.GET.get("routineId"))
            except (ValueError, TypeError):
                messages.error(request, "ID de rutina inválido")
                routine_id = None

        date_filter = None
        if request.GET.get("date"):
            try:
                from datetime import datetime

                date_filter = datetime.strptime(request.GET.get("date"), "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Formato de fecha inválido. Use YYYY-MM-DD")
                date_filter = None

        try:
            # Obtener sesiones usando el servicio
            sessions = list_sessions_service(
                user=request.user,
                routine_id=routine_id,
                date_filter=date_filter,
            )

            # Serializar sesiones
            serializer = SessionSerializer(sessions, many=True)
            sessions_data = serializer.data

            # Obtener rutinas del usuario para el filtro
            from apps.routines.services import list_routines_service

            routines = list_routines_service(user=request.user)
            from apps.routines.serializers import RoutineSerializer

            routines_serializer = RoutineSerializer(routines, many=True)

            context = {
                "sessions": sessions_data,
                "routines": routines_serializer.data,
                "routine_id": routine_id,
                "date_filter": date_filter.isoformat() if date_filter else None,
            }

            return render(request, "sessions/list.html", context)

        except Exception as error:
            messages.error(request, f"Error al cargar sesiones: {error!s}")
            return render(request, "sessions/list.html", {"sessions": []})


class SessionDetailView(View):
    """Vista para ver el detalle de una sesión completa con ejercicios."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Muestra el detalle de una sesión con toda su información y ejercicios."""
        try:
            # Obtener sesión usando el servicio
            session = get_session_full_service(session_id=pk, user=request.user)
            serializer = SessionFullSerializer(session)
            session_data = serializer.data

            context = {
                "session": session_data,
            }

            return render(request, "sessions/detail.html", context)

        except NotFound:
            messages.error(request, "Sesión no encontrada.")
            return redirect("sessions:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para ver esta sesión.")
            return redirect("sessions:list")
        except Exception as error:
            messages.error(request, f"Error al cargar sesión: {error!s}")
            return redirect("sessions:list")


class SessionCreateView(View):
    """Vista para crear una nueva sesión."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra el formulario de creación."""
        # Obtener routine_id de query params si existe (para vincular desde rutina)
        routine_id = request.GET.get("routineId")
        form = SessionCreateForm(user=request.user)

        # Pre-seleccionar rutina si se proporciona
        if routine_id:
            try:
                from apps.routines.repositories import get_routine_by_id_repository

                routine = get_routine_by_id_repository(routine_id=int(routine_id))
                if routine and routine.created_by.id == request.user.id:
                    form.fields["routine"].initial = routine.id
            except Exception:
                pass  # Si no se puede obtener la rutina, simplemente no pre-seleccionar

        return render(request, "sessions/form.html", {"form": form, "action": "create"})

    @method_decorator(login_required)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Procesa el formulario de creación."""
        form = SessionCreateForm(request.POST, user=request.user)

        if not form.is_valid():
            return render(request, "sessions/form.html", {"form": form, "action": "create"})

        try:
            # Preparar datos para el servicio
            validated_data = {"date": form.cleaned_data["date"]}

            if form.cleaned_data.get("routine"):
                validated_data["routineId"] = form.cleaned_data["routine"].id
            if form.cleaned_data.get("start_time"):
                validated_data["startTime"] = form.cleaned_data["start_time"]
            if form.cleaned_data.get("end_time"):
                validated_data["endTime"] = form.cleaned_data["end_time"]
            if form.cleaned_data.get("notes"):
                validated_data["notes"] = form.cleaned_data["notes"]
            if form.cleaned_data.get("rpe") is not None:
                validated_data["rpe"] = form.cleaned_data["rpe"]
            if form.cleaned_data.get("energy_level"):
                validated_data["energyLevel"] = form.cleaned_data["energy_level"]
            if form.cleaned_data.get("sleep_hours") is not None:
                validated_data["sleepHours"] = form.cleaned_data["sleep_hours"]

            # Crear sesión usando el servicio
            session = create_session_service(validated_data=validated_data, user=request.user)

            messages.success(request, f"Sesión del {session.date} creada correctamente.")
            return redirect("sessions:detail", pk=session.id)

        except Exception as error:
            messages.error(request, f"Error al crear sesión: {error!s}")
            return render(request, "sessions/form.html", {"form": form, "action": "create"})


class SessionUpdateView(View):
    """Vista para actualizar una sesión existente."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Muestra el formulario de actualización."""
        try:
            # Obtener sesión usando el servicio
            session = get_session_full_service(session_id=pk, user=request.user)
            serializer = SessionSerializer(session)
            session_data = serializer.data

            # Preparar datos iniciales para el formulario
            form = SessionUpdateForm(
                initial={
                    "date": session_data.get("date"),
                    "routine": session_data.get("routineId"),
                    "start_time": session_data.get("startTime"),
                    "end_time": session_data.get("endTime"),
                    "notes": session_data.get("notes"),
                    "rpe": session_data.get("rpe"),
                    "energy_level": session_data.get("energyLevel"),
                    "sleep_hours": session_data.get("sleepHours"),
                },
                user=request.user,
            )

            context = {
                "form": form,
                "session": session_data,
                "action": "update",
            }

            return render(request, "sessions/form.html", context)

        except NotFound:
            messages.error(request, "Sesión no encontrada.")
            return redirect("sessions:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para editar esta sesión.")
            return redirect("sessions:list")
        except Exception as error:
            messages.error(request, f"Error al cargar sesión: {error!s}")
            return redirect("sessions:list")

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Procesa el formulario de actualización."""
        form = SessionUpdateForm(request.POST, user=request.user)

        if not form.is_valid():
            try:
                session = get_session_full_service(session_id=pk, user=request.user)
                serializer = SessionSerializer(session)
                session_data = serializer.data
            except Exception:
                session_data = {}
            return render(
                request,
                "sessions/form.html",
                {"form": form, "session": session_data, "action": "update"},
            )

        try:
            # Preparar datos para el servicio
            validated_data = {}
            if form.cleaned_data.get("date"):
                validated_data["date"] = form.cleaned_data["date"]
            if form.cleaned_data.get("routine"):
                validated_data["routineId"] = form.cleaned_data["routine"].id
            elif "routine" in form.cleaned_data:
                validated_data["routineId"] = None
            if form.cleaned_data.get("start_time") is not None:
                validated_data["startTime"] = form.cleaned_data["start_time"]
            if form.cleaned_data.get("end_time") is not None:
                validated_data["endTime"] = form.cleaned_data["end_time"]
            if "notes" in form.cleaned_data:
                validated_data["notes"] = form.cleaned_data["notes"] or None
            if form.cleaned_data.get("rpe") is not None:
                validated_data["rpe"] = form.cleaned_data["rpe"]
            if form.cleaned_data.get("energy_level"):
                validated_data["energyLevel"] = form.cleaned_data["energy_level"]
            elif "energy_level" in form.cleaned_data:
                validated_data["energyLevel"] = None
            if form.cleaned_data.get("sleep_hours") is not None:
                validated_data["sleepHours"] = form.cleaned_data["sleep_hours"]

            # Actualizar sesión usando el servicio
            updated_session = update_session_service(
                session_id=pk, validated_data=validated_data, user=request.user
            )

            messages.success(
                request, f"Sesión del {updated_session.date} actualizada correctamente."
            )
            return redirect("sessions:detail", pk=pk)

        except NotFound:
            messages.error(request, "Sesión no encontrada.")
            return redirect("sessions:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para editar esta sesión.")
            return redirect("sessions:list")
        except Exception as error:
            messages.error(request, f"Error al actualizar sesión: {error!s}")
            return redirect("sessions:detail", pk=pk)


class SessionDeleteView(View):
    """Vista para eliminar una sesión."""

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Elimina una sesión."""
        try:
            # Obtener sesión usando el servicio para verificar permisos
            session = get_session_full_service(session_id=pk, user=request.user)

            # Eliminar sesión usando el servicio
            delete_session_service(session_id=pk, user=request.user)

            messages.success(request, f"Sesión del {session.date} eliminada correctamente.")
            return redirect("sessions:list")

        except NotFound:
            messages.error(request, "Sesión no encontrada.")
            return redirect("sessions:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para eliminar esta sesión.")
            return redirect("sessions:list")
        except Exception as error:
            messages.error(request, f"Error al eliminar sesión: {error!s}")
            return redirect("sessions:detail", pk=pk)


class SessionExerciseCreateView(View):
    """Vista para crear un ejercicio en una sesión."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Muestra el formulario de creación de ejercicio en sesión."""
        try:
            # Verificar que la sesión existe y pertenece al usuario
            session = get_session_full_service(session_id=pk, user=request.user)
            serializer = SessionSerializer(session)
            session_data = serializer.data

            form = SessionExerciseForm()
            context = {
                "form": form,
                "session_id": pk,
                "session": session_data,
            }
            return render(request, "sessions/exercise_form.html", context)
        except NotFound:
            messages.error(request, "Sesión no encontrada.")
            return redirect("sessions:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para añadir ejercicios a esta sesión.")
            return redirect("sessions:list")
        except Exception as error:
            messages.error(request, f"Error al cargar sesión: {error!s}")
            return redirect("sessions:list")

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Procesa el formulario de creación de ejercicio en sesión."""
        form = SessionExerciseForm(request.POST)

        if not form.is_valid():
            try:
                session = get_session_full_service(session_id=pk, user=request.user)
                serializer = SessionSerializer(session)
                session_data = serializer.data
            except Exception:
                session_data = {}
            return render(
                request,
                "sessions/exercise_form.html",
                {"form": form, "session_id": pk, "session": session_data},
            )

        try:
            # Preparar datos para el servicio
            validated_data = {
                "exerciseId": form.cleaned_data["exercise"].id,
            }
            if form.cleaned_data.get("order") is not None:
                validated_data["order"] = form.cleaned_data["order"]
            if form.cleaned_data.get("sets_completed") is not None:
                validated_data["setsCompleted"] = form.cleaned_data["sets_completed"]
            if form.cleaned_data.get("repetitions"):
                validated_data["repetitions"] = form.cleaned_data["repetitions"]
            if form.cleaned_data.get("weight") is not None:
                validated_data["weight"] = form.cleaned_data["weight"]
            if form.cleaned_data.get("rpe") is not None:
                validated_data["rpe"] = form.cleaned_data["rpe"]
            if form.cleaned_data.get("rest_seconds") is not None:
                validated_data["restSeconds"] = form.cleaned_data["rest_seconds"]
            if form.cleaned_data.get("notes"):
                validated_data["notes"] = form.cleaned_data["notes"]

            # Crear ejercicio en sesión usando el servicio
            create_session_exercise_service(
                session_id=pk, validated_data=validated_data, user=request.user
            )

            messages.success(request, "Ejercicio añadido a la sesión correctamente.")
            return redirect("sessions:detail", pk=pk)

        except NotFound:
            messages.error(request, "Sesión o ejercicio no encontrado.")
            return redirect("sessions:detail", pk=pk)
        except PermissionDenied:
            messages.error(request, "No tienes permisos para añadir ejercicios a esta sesión.")
            return redirect("sessions:detail", pk=pk)
        except Exception as error:
            messages.error(request, f"Error al añadir ejercicio: {error!s}")
            try:
                session = get_session_full_service(session_id=pk, user=request.user)
                serializer = SessionSerializer(session)
                session_data = serializer.data
            except Exception:
                session_data = {}
            return render(
                request,
                "sessions/exercise_form.html",
                {"form": form, "session_id": pk, "session": session_data},
            )


class SessionExerciseUpdateView(View):
    """Vista para actualizar un ejercicio en una sesión."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int, exerciseId: int) -> HttpResponse:
        """Muestra el formulario de actualización de ejercicio en sesión."""
        try:
            # Verificar que la sesión existe y pertenece al usuario
            session = get_session_full_service(session_id=pk, user=request.user)
            serializer = SessionSerializer(session)
            session_data = serializer.data

            # Obtener ejercicio de sesión
            session_exercise = get_session_exercise_service(
                session_exercise_id=exerciseId, user=request.user
            )
            if session_exercise.session.id != pk:
                messages.error(request, "Ejercicio no encontrado en esta sesión.")
                return redirect("sessions:detail", pk=pk)

            from apps.sessions.serializers import SessionExerciseSerializer

            exercise_serializer = SessionExerciseSerializer(session_exercise)
            exercise_data = exercise_serializer.data

            form = SessionExerciseForm(
                initial={
                    "exercise": exercise_data.get("exerciseId"),
                    "order": exercise_data.get("order"),
                    "sets_completed": exercise_data.get("setsCompleted"),
                    "repetitions": exercise_data.get("repetitions"),
                    "weight": exercise_data.get("weight"),
                    "rpe": exercise_data.get("rpe"),
                    "rest_seconds": exercise_data.get("restSeconds"),
                    "notes": exercise_data.get("notes"),
                }
            )

            context = {
                "form": form,
                "session_id": pk,
                "exercise_id": exerciseId,
                "session": session_data,
                "exercise": exercise_data,
                "action": "update",
            }
            return render(request, "sessions/exercise_form.html", context)
        except NotFound:
            messages.error(request, "Sesión o ejercicio no encontrado.")
            return redirect("sessions:detail", pk=pk)
        except PermissionDenied:
            messages.error(request, "No tienes permisos para editar ejercicios de esta sesión.")
            return redirect("sessions:detail", pk=pk)
        except Exception as error:
            messages.error(request, f"Error al cargar ejercicio: {error!s}")
            return redirect("sessions:detail", pk=pk)

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int, exerciseId: int) -> HttpResponse:
        """Procesa el formulario de actualización de ejercicio en sesión."""
        form = SessionExerciseForm(request.POST)

        if not form.is_valid():
            try:
                session = get_session_full_service(session_id=pk, user=request.user)
                serializer = SessionSerializer(session)
                session_data = serializer.data
            except Exception:
                session_data = {}
            return render(
                request,
                "sessions/exercise_form.html",
                {
                    "form": form,
                    "session_id": pk,
                    "exercise_id": exerciseId,
                    "session": session_data,
                    "action": "update",
                },
            )

        try:
            # Preparar datos para el servicio
            validated_data = {}
            if form.cleaned_data.get("exercise"):
                validated_data["exerciseId"] = form.cleaned_data["exercise"].id
            if form.cleaned_data.get("order") is not None:
                validated_data["order"] = form.cleaned_data["order"]
            if form.cleaned_data.get("sets_completed") is not None:
                validated_data["setsCompleted"] = form.cleaned_data["sets_completed"]
            if form.cleaned_data.get("repetitions"):
                validated_data["repetitions"] = form.cleaned_data["repetitions"]
            if form.cleaned_data.get("weight") is not None:
                validated_data["weight"] = form.cleaned_data["weight"]
            if form.cleaned_data.get("rpe") is not None:
                validated_data["rpe"] = form.cleaned_data["rpe"]
            if form.cleaned_data.get("rest_seconds") is not None:
                validated_data["restSeconds"] = form.cleaned_data["rest_seconds"]
            if form.cleaned_data.get("notes"):
                validated_data["notes"] = form.cleaned_data["notes"]

            # Actualizar ejercicio en sesión usando el servicio
            update_session_exercise_service(
                session_exercise_id=exerciseId, validated_data=validated_data, user=request.user
            )

            messages.success(request, "Ejercicio actualizado correctamente.")
            return redirect("sessions:detail", pk=pk)

        except NotFound:
            messages.error(request, "Sesión o ejercicio no encontrado.")
            return redirect("sessions:detail", pk=pk)
        except PermissionDenied:
            messages.error(request, "No tienes permisos para editar ejercicios de esta sesión.")
            return redirect("sessions:detail", pk=pk)
        except Exception as error:
            messages.error(request, f"Error al actualizar ejercicio: {error!s}")
            return redirect("sessions:detail", pk=pk)


class SessionExerciseDeleteView(View):
    """Vista para eliminar un ejercicio de una sesión."""

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int, exerciseId: int) -> HttpResponse:
        """Elimina un ejercicio de una sesión."""
        try:
            # Verificar que el ejercicio pertenece a la sesión
            session_exercise = get_session_exercise_service(
                session_exercise_id=exerciseId, user=request.user
            )
            if session_exercise.session.id != pk:
                messages.error(request, "Ejercicio no encontrado en esta sesión.")
                return redirect("sessions:detail", pk=pk)

            # Eliminar ejercicio usando el servicio
            delete_session_exercise_service(session_exercise_id=exerciseId, user=request.user)

            messages.success(request, "Ejercicio eliminado de la sesión correctamente.")
            return redirect("sessions:detail", pk=pk)

        except NotFound:
            messages.error(request, "Ejercicio no encontrado.")
            return redirect("sessions:detail", pk=pk)
        except PermissionDenied:
            messages.error(request, "No tienes permisos para eliminar ejercicios de esta sesión.")
            return redirect("sessions:detail", pk=pk)
        except Exception as error:
            messages.error(request, f"Error al eliminar ejercicio: {error!s}")
            return redirect("sessions:detail", pk=pk)
