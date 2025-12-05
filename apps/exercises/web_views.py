from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.exercises.forms import ExerciseCreateForm, ExerciseUpdateForm
from apps.exercises.models import Exercise
from apps.exercises.serializers import ExerciseSerializer
from apps.exercises.services import (
    create_exercise_service,
    delete_exercise_service,
    get_exercise_service,
    list_exercises_service,
    update_exercise_service,
)

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


class ExerciseListView(View):
    """Vista para listar ejercicios."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra la lista de ejercicios con filtros."""
        # Extraer filtros de query params
        filters = {}
        primary_muscle_group = request.GET.get("primaryMuscleGroup", "").strip()
        if primary_muscle_group:
            filters["primaryMuscleGroup"] = primary_muscle_group

        equipment = request.GET.get("equipment", "").strip()
        if equipment:
            filters["equipment"] = equipment

        difficulty = request.GET.get("difficulty", "").strip()
        if difficulty:
            filters["difficulty"] = difficulty

        is_active_param = request.GET.get("isActive", "").strip()
        if is_active_param:
            is_active_str = is_active_param.lower()
            filters["isActive"] = is_active_str in ["true", "1", "yes"]

        search = request.GET.get("search", "").strip()
        ordering = request.GET.get("ordering", "name")

        try:
            # Obtener ejercicios usando el servicio
            exercises = list_exercises_service(
                filters=filters if filters else None,
                search=search if search else None,
                ordering=ordering,
                user=request.user if request.user.is_authenticated else None,
            )

            # Serializar ejercicios
            serializer = ExerciseSerializer(exercises, many=True)
            exercises_data = serializer.data

            # Preparar valores para el contexto (para mantener los valores en el formulario)
            context_filters = {
                "primaryMuscleGroup": primary_muscle_group,
                "equipment": equipment,
                "difficulty": difficulty,
                "isActive": is_active_param if is_active_param else None,
            }

            context = {
                "exercises": exercises_data,
                "filters": context_filters,
                "search": search,
                "ordering": ordering,
                "movement_types": [("", "---------"), *Exercise.MOVEMENT_TYPE_CHOICES],
                "muscle_groups": Exercise.PRIMARY_MUSCLE_GROUP_CHOICES,
                "equipment_choices": Exercise.EQUIPMENT_CHOICES,
                "difficulty_choices": Exercise.DIFFICULTY_CHOICES,
            }

            return render(request, "exercises/list.html", context)

        except Exception as error:
            messages.error(request, f"Error al cargar ejercicios: {error!s}")
            # Preparar contexto mínimo en caso de error
            context_filters = {
                "primaryMuscleGroup": request.GET.get("primaryMuscleGroup", ""),
                "equipment": request.GET.get("equipment", ""),
                "difficulty": request.GET.get("difficulty", ""),
                "isActive": None,
            }
            return render(
                request,
                "exercises/list.html",
                {
                    "exercises": [],
                    "filters": context_filters,
                    "search": request.GET.get("search", ""),
                    "movement_types": [("", "---------"), *Exercise.MOVEMENT_TYPE_CHOICES],
                    "muscle_groups": Exercise.PRIMARY_MUSCLE_GROUP_CHOICES,
                    "equipment_choices": Exercise.EQUIPMENT_CHOICES,
                    "difficulty_choices": Exercise.DIFFICULTY_CHOICES,
                },
            )


class ExerciseDetailView(View):
    """Vista para ver el detalle de un ejercicio."""

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Muestra el detalle de un ejercicio."""
        try:
            # Obtener ejercicio usando el servicio
            exercise = get_exercise_service(exercise_id=pk)

            # Serializar ejercicio
            serializer = ExerciseSerializer(exercise)
            exercise_data = serializer.data

            # Verificar si el usuario es el creador
            is_owner = (
                request.user.is_authenticated
                and exercise.created_by
                and exercise.created_by.id == request.user.id
            )

            context = {
                "exercise": exercise_data,
                "is_owner": is_owner,
            }

            return render(request, "exercises/detail.html", context)

        except NotFound:
            messages.error(request, "Ejercicio no encontrado.")
            return redirect("exercises:list")
        except Exception as error:
            messages.error(request, f"Error al cargar ejercicio: {error!s}")
            return redirect("exercises:list")


class ExerciseCreateView(View):
    """Vista para crear un nuevo ejercicio."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra el formulario de creación."""
        form = ExerciseCreateForm()
        return render(request, "exercises/form.html", {"form": form, "action": "create"})

    @method_decorator(login_required)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Procesa el formulario de creación."""
        form = ExerciseCreateForm(request.POST)

        if not form.is_valid():
            return render(request, "exercises/form.html", {"form": form, "action": "create"})

        try:
            # Preparar datos para el servicio (solo incluir campos con valores)
            validated_data = {"name": form.cleaned_data["name"]}

            if form.cleaned_data.get("description"):
                validated_data["description"] = form.cleaned_data["description"]
            if form.cleaned_data.get("movement_type"):
                validated_data["movementType"] = form.cleaned_data["movement_type"]
            if form.cleaned_data.get("primary_muscle_group"):
                validated_data["primaryMuscleGroup"] = form.cleaned_data["primary_muscle_group"]
            if form.cleaned_data.get("equipment"):
                validated_data["equipment"] = form.cleaned_data["equipment"]
            if form.cleaned_data.get("difficulty"):
                validated_data["difficulty"] = form.cleaned_data["difficulty"]
            if form.cleaned_data.get("instructions"):
                validated_data["instructions"] = form.cleaned_data["instructions"]
            if form.cleaned_data.get("image_url"):
                validated_data["imageUrl"] = form.cleaned_data["image_url"]
            if form.cleaned_data.get("video_url"):
                validated_data["videoUrl"] = form.cleaned_data["video_url"]

            validated_data["isActive"] = form.cleaned_data.get("is_active", True)

            # Crear ejercicio usando el servicio
            exercise = create_exercise_service(validated_data=validated_data, user=request.user)

            messages.success(request, f"Ejercicio '{exercise.name}' creado correctamente.")
            return redirect("exercises:detail", pk=exercise.id)

        except Exception as error:
            messages.error(request, f"Error al crear ejercicio: {error!s}")
            return render(request, "exercises/form.html", {"form": form, "action": "create"})


class ExerciseUpdateView(View):
    """Vista para actualizar un ejercicio existente."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Muestra el formulario de actualización."""
        try:
            # Obtener ejercicio usando el servicio
            exercise = get_exercise_service(exercise_id=pk)

            # Verificar permisos
            if exercise.created_by and exercise.created_by.id != request.user.id:
                messages.error(request, "No tienes permisos para editar este ejercicio.")
                return redirect("exercises:detail", pk=pk)

            # Serializar ejercicio
            serializer = ExerciseSerializer(exercise)
            exercise_data = serializer.data

            # Preparar datos iniciales para el formulario
            form = ExerciseUpdateForm(
                initial={
                    "name": exercise_data.get("name"),
                    "description": exercise_data.get("description"),
                    "movement_type": exercise_data.get("movementType"),
                    "primary_muscle_group": exercise_data.get("primaryMuscleGroup"),
                    "equipment": exercise_data.get("equipment"),
                    "difficulty": exercise_data.get("difficulty"),
                    "instructions": exercise_data.get("instructions"),
                    "image_url": exercise_data.get("imageUrl"),
                    "video_url": exercise_data.get("videoUrl"),
                    "is_active": exercise_data.get("isActive"),
                }
            )

            context = {
                "form": form,
                "exercise": exercise_data,
                "action": "update",
            }

            return render(request, "exercises/form.html", context)

        except NotFound:
            messages.error(request, "Ejercicio no encontrado.")
            return redirect("exercises:list")
        except Exception as error:
            messages.error(request, f"Error al cargar ejercicio: {error!s}")
            return redirect("exercises:list")

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Procesa el formulario de actualización."""
        form = ExerciseUpdateForm(request.POST)

        if not form.is_valid():
            try:
                exercise = get_exercise_service(exercise_id=pk)
                serializer = ExerciseSerializer(exercise)
                exercise_data = serializer.data
            except Exception:
                exercise_data = {}
            return render(
                request,
                "exercises/form.html",
                {"form": form, "exercise": exercise_data, "action": "update"},
            )

        try:
            # Obtener ejercicio usando el servicio
            exercise = get_exercise_service(exercise_id=pk)

            # Verificar permisos
            if exercise.created_by and exercise.created_by.id != request.user.id:
                messages.error(request, "No tienes permisos para editar este ejercicio.")
                return redirect("exercises:detail", pk=pk)

            # Preparar datos para el servicio (solo campos proporcionados)
            validated_data = {}
            if form.cleaned_data.get("name"):
                validated_data["name"] = form.cleaned_data["name"]
            if form.cleaned_data.get("description") is not None:
                validated_data["description"] = form.cleaned_data["description"] or None
            if form.cleaned_data.get("movement_type"):
                validated_data["movementType"] = form.cleaned_data["movement_type"] or None
            if form.cleaned_data.get("primary_muscle_group"):
                validated_data["primaryMuscleGroup"] = (
                    form.cleaned_data["primary_muscle_group"] or None
                )
            if form.cleaned_data.get("equipment"):
                validated_data["equipment"] = form.cleaned_data["equipment"] or None
            if form.cleaned_data.get("difficulty"):
                validated_data["difficulty"] = form.cleaned_data["difficulty"] or None
            if form.cleaned_data.get("instructions") is not None:
                validated_data["instructions"] = form.cleaned_data["instructions"] or None
            if form.cleaned_data.get("image_url") is not None:
                validated_data["imageUrl"] = form.cleaned_data["image_url"] or None
            if form.cleaned_data.get("video_url") is not None:
                validated_data["videoUrl"] = form.cleaned_data["video_url"] or None
            if "is_active" in form.cleaned_data:
                validated_data["isActive"] = form.cleaned_data["is_active"]

            # Actualizar ejercicio usando el servicio
            updated_exercise = update_exercise_service(
                exercise_id=pk, validated_data=validated_data, user=request.user
            )

            messages.success(
                request, f"Ejercicio '{updated_exercise.name}' actualizado correctamente."
            )
            return redirect("exercises:detail", pk=pk)

        except NotFound:
            messages.error(request, "Ejercicio no encontrado.")
            return redirect("exercises:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para editar este ejercicio.")
            return redirect("exercises:list")
        except Exception as error:
            messages.error(request, f"Error al actualizar ejercicio: {error!s}")
            return redirect("exercises:detail", pk=pk)


class ExerciseDeleteView(View):
    """Vista para eliminar un ejercicio (soft delete)."""

    @method_decorator(login_required)
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Elimina un ejercicio."""
        try:
            # Obtener ejercicio usando el servicio
            exercise = get_exercise_service(exercise_id=pk)

            # Verificar permisos
            if exercise.created_by and exercise.created_by.id != request.user.id:
                messages.error(request, "No tienes permisos para eliminar este ejercicio.")
                return redirect("exercises:detail", pk=pk)

            # Eliminar ejercicio usando el servicio
            delete_exercise_service(exercise_id=pk, user=request.user)

            messages.success(request, f"Ejercicio '{exercise.name}' eliminado correctamente.")
            return redirect("exercises:list")

        except NotFound:
            messages.error(request, "Ejercicio no encontrado.")
            return redirect("exercises:list")
        except PermissionDenied:
            messages.error(request, "No tienes permisos para eliminar este ejercicio.")
            return redirect("exercises:list")
        except Exception as error:
            messages.error(request, f"Error al eliminar ejercicio: {error!s}")
            return redirect("exercises:detail", pk=pk)
