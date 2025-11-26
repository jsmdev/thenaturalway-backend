from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.exercises.serializers import (
    ExerciseSerializer,
    ExerciseCreateSerializer,
    ExerciseUpdateSerializer,
)
from apps.exercises.services import (
    list_exercises_service,
    get_exercise_service,
    create_exercise_service,
    update_exercise_service,
    delete_exercise_service,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


class ExerciseListAPIView(APIView):
    """Endpoint para listar y crear ejercicios."""

    def get_permissions(self):
        """Permisos diferentes según el método HTTP."""
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request: Request) -> Response:
        """Lista ejercicios con filtros y búsqueda."""
        try:
            # Extraer query params
            filters = {}
            if request.query_params.get("primaryMuscleGroup"):
                filters["primaryMuscleGroup"] = request.query_params.get("primaryMuscleGroup")
            if request.query_params.get("equipment"):
                filters["equipment"] = request.query_params.get("equipment")
            if request.query_params.get("difficulty"):
                filters["difficulty"] = request.query_params.get("difficulty")
            if request.query_params.get("isActive") is not None:
                is_active_str = request.query_params.get("isActive", "").lower()
                filters["isActive"] = is_active_str in ["true", "1", "yes"]
            if request.query_params.get("createdBy"):
                filters["createdBy"] = request.query_params.get("createdBy")

            search = request.query_params.get("search")
            ordering = request.query_params.get("ordering")

            # Llamar al servicio
            exercises = list_exercises_service(
                filters=filters if filters else None,
                search=search,
                ordering=ordering,
                user=request.user if request.user.is_authenticated else None,
            )

            # Serializar datos
            serializer = ExerciseSerializer(exercises, many=True)

            return Response(
                {
                    "data": serializer.data,
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as error:
            return Response(
                {
                    "error": "Validation error",
                    "message": error.detail,
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            return Response(
                {
                    "error": "Internal server error",
                    "message": str(error),
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request: Request) -> Response:
        """Crea un nuevo ejercicio (requiere autenticación)."""
        serializer = ExerciseCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation error",
                    "message": serializer.errors,
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Llamar al servicio (el usuario está autenticado por permisos)
            exercise = create_exercise_service(
                validated_data=serializer.validated_data, user=request.user
            )

            # Serializar respuesta
            response_serializer = ExerciseSerializer(exercise)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Ejercicio creado correctamente",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as error:
            return Response(
                {
                    "error": "Validation error",
                    "message": error.detail,
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            return Response(
                {
                    "error": "Internal server error",
                    "message": str(error),
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ExerciseDetailAPIView(APIView):
    """Endpoint para obtener, actualizar y eliminar un ejercicio específico."""

    def get_permissions(self):
        """Permisos diferentes según el método HTTP."""
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request: Request, pk: int) -> Response:
        """Obtiene el detalle de un ejercicio."""
        try:
            # Llamar al servicio
            exercise = get_exercise_service(exercise_id=pk)

            # Serializar respuesta
            serializer = ExerciseSerializer(exercise)

            return Response(
                {
                    "data": serializer.data,
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_200_OK,
            )
        except NotFound:
            return Response(
                {
                    "error": "Not found",
                    "message": "Ejercicio no encontrado",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as error:
            return Response(
                {
                    "error": "Internal server error",
                    "message": str(error),
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request: Request, pk: int) -> Response:
        """Actualiza un ejercicio existente (requiere autenticación y ser el creador)."""
        serializer = ExerciseUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation error",
                    "message": serializer.errors,
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Llamar al servicio
            exercise = update_exercise_service(
                exercise_id=pk,
                validated_data=serializer.validated_data,
                user=request.user,
            )

            # Serializar respuesta
            response_serializer = ExerciseSerializer(exercise)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Ejercicio actualizado correctamente",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_200_OK,
            )
        except NotFound:
            return Response(
                {
                    "error": "Not found",
                    "message": "Ejercicio no encontrado",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionDenied:
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Solo el creador puede actualizar este ejercicio",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as error:
            return Response(
                {
                    "error": "Validation error",
                    "message": error.detail,
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            return Response(
                {
                    "error": "Internal server error",
                    "message": str(error),
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request: Request, pk: int) -> Response:
        """Elimina un ejercicio (soft delete, requiere autenticación y ser el creador)."""
        try:
            # Llamar al servicio
            delete_exercise_service(exercise_id=pk, user=request.user)

            return Response(
                {
                    "message": "Ejercicio eliminado correctamente",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except NotFound:
            return Response(
                {
                    "error": "Not found",
                    "message": "Ejercicio no encontrado",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionDenied:
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Solo el creador puede eliminar este ejercicio",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as error:
            return Response(
                {
                    "error": "Internal server error",
                    "message": str(error),
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

