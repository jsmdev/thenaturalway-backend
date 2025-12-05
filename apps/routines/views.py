from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.routines.serializers import (
    BlockCreateSerializer,
    BlockSerializer,
    DayCreateSerializer,
    DaySerializer,
    RoutineCreateSerializer,
    RoutineExerciseCreateSerializer,
    RoutineExerciseSerializer,
    RoutineFullSerializer,
    RoutineSerializer,
    RoutineUpdateSerializer,
    WeekCreateSerializer,
    WeekSerializer,
)
from apps.routines.services import (
    create_block_service,
    create_day_service,
    create_routine_exercise_service,
    create_routine_service,
    create_week_service,
    delete_routine_service,
    get_routine_full_service,
    get_routine_service,
    list_routines_service,
    update_routine_service,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


class RoutineListAPIView(APIView):
    """Endpoint para listar y crear rutinas."""

    permission_classes: ClassVar[list] = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Lista rutinas del usuario autenticado."""
        try:
            routines = list_routines_service(user=request.user)
            serializer = RoutineSerializer(routines, many=True)

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
        """Crea una nueva rutina."""
        serializer = RoutineCreateSerializer(data=request.data)

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
            routine = create_routine_service(
                validated_data=serializer.validated_data, user=request.user
            )
            response_serializer = RoutineSerializer(routine)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Rutina creada correctamente",
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


class RoutineDetailAPIView(APIView):
    """Endpoint para obtener, actualizar y eliminar una rutina específica."""

    permission_classes: ClassVar[list] = [IsAuthenticated]

    def get(self, request: Request, pk: int) -> Response:
        """Obtiene el detalle de una rutina (opcionalmente con jerarquía completa)."""
        try:
            include_full = request.query_params.get("full", "").lower() == "true"

            if include_full:
                routine = get_routine_full_service(routine_id=pk, user=request.user)
                serializer = RoutineFullSerializer(routine)
            else:
                routine = get_routine_service(routine_id=pk, user=request.user)
                serializer = RoutineSerializer(routine)

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
                    "message": "Rutina no encontrada",
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
        """Actualiza una rutina existente."""
        serializer = RoutineUpdateSerializer(data=request.data)

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
            routine = update_routine_service(
                routine_id=pk,
                validated_data=serializer.validated_data,
                user=request.user,
            )
            response_serializer = RoutineSerializer(routine)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Rutina actualizada correctamente",
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
                    "message": "Rutina no encontrada",
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
                    "message": "Solo el creador puede actualizar esta rutina",
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
        """Elimina una rutina (soft delete)."""
        try:
            delete_routine_service(routine_id=pk, user=request.user)

            return Response(
                {
                    "message": "Rutina eliminada correctamente",
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
                    "message": "Rutina no encontrada",
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
                    "message": "Solo el creador puede eliminar esta rutina",
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


# Vistas API anidadas
class WeekCreateAPIView(APIView):
    """Endpoint para crear una semana en una rutina."""

    permission_classes: ClassVar[list] = [IsAuthenticated]

    def post(self, request: Request, pk: int) -> Response:
        """Crea una nueva semana en la rutina."""
        serializer = WeekCreateSerializer(data=request.data)

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
            week = create_week_service(
                routine_id=pk, validated_data=serializer.validated_data, user=request.user
            )
            response_serializer = WeekSerializer(week)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Semana creada correctamente",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except NotFound:
            return Response(
                {
                    "error": "Not found",
                    "message": "Rutina no encontrada",
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
                    "message": "Solo el creador puede añadir semanas a esta rutina",
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


class DayCreateAPIView(APIView):
    """Endpoint para crear un día en una semana."""

    permission_classes: ClassVar[list] = [IsAuthenticated]

    def post(self, request: Request, pk: int, weekId: int) -> Response:
        """Crea un nuevo día en la semana."""
        serializer = DayCreateSerializer(data=request.data)

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
            day = create_day_service(
                week_id=weekId, validated_data=serializer.validated_data, user=request.user
            )
            response_serializer = DaySerializer(day)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Día creado correctamente",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except NotFound:
            return Response(
                {
                    "error": "Not found",
                    "message": "Semana no encontrada",
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
                    "message": "Solo el creador puede añadir días a esta rutina",
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


class BlockCreateAPIView(APIView):
    """Endpoint para crear un bloque en un día."""

    permission_classes: ClassVar[list] = [IsAuthenticated]

    def post(self, request: Request, pk: int, dayId: int) -> Response:
        """Crea un nuevo bloque en el día."""
        serializer = BlockCreateSerializer(data=request.data)

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
            block = create_block_service(
                day_id=dayId, validated_data=serializer.validated_data, user=request.user
            )
            response_serializer = BlockSerializer(block)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Bloque creado correctamente",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except NotFound:
            return Response(
                {
                    "error": "Not found",
                    "message": "Día no encontrado",
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
                    "message": "Solo el creador puede añadir bloques a esta rutina",
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


class RoutineExerciseCreateAPIView(APIView):
    """Endpoint para crear un ejercicio en un bloque."""

    permission_classes: ClassVar[list] = [IsAuthenticated]

    def post(self, request: Request, pk: int, blockId: int) -> Response:
        """Crea un nuevo ejercicio en el bloque."""
        serializer = RoutineExerciseCreateSerializer(data=request.data)

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
            exercise_id = serializer.validated_data.pop("exerciseId")
            routine_exercise = create_routine_exercise_service(
                block_id=blockId,
                exercise_id=exercise_id,
                validated_data=serializer.validated_data,
                user=request.user,
            )
            response_serializer = RoutineExerciseSerializer(routine_exercise)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Ejercicio añadido a la rutina correctamente",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except NotFound:
            return Response(
                {
                    "error": "Not found",
                    "message": "Bloque o ejercicio no encontrado",
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
                    "message": "Solo el creador puede añadir ejercicios a esta rutina",
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
