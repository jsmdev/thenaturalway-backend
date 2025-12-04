from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.sessions.serializers import (
    SessionSerializer,
    SessionCreateSerializer,
    SessionUpdateSerializer,
    SessionFullSerializer,
    SessionExerciseSerializer,
    SessionExerciseCreateSerializer,
    SessionExerciseUpdateSerializer,
)
from apps.sessions.services import (
    list_sessions_service,
    get_session_service,
    get_session_full_service,
    create_session_service,
    update_session_service,
    delete_session_service,
    list_session_exercises_service,
    get_session_exercise_service,
    create_session_exercise_service,
    update_session_exercise_service,
    delete_session_exercise_service,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


class SessionListAPIView(APIView):
    """
    Endpoint para listar y crear sesiones.

    Endpoints:
    - GET /api/sessions/ - Lista sesiones del usuario autenticado con filtros
    - POST /api/sessions/ - Crea una nueva sesión (requiere autenticación)

    Permisos:
    - GET: Requiere autenticación (IsAuthenticated)
    - POST: Requiere autenticación (IsAuthenticated)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: "Request") -> Response:
        """
        Lista sesiones del usuario autenticado con filtros.

        Query Parameters:
        - routineId (int, opcional): Filtra por ID de rutina
        - date (date, opcional): Filtra por fecha (formato: YYYY-MM-DD)

        Respuestas:
        - 200 OK: Lista de sesiones
        - 400 Bad Request: Error de validación en filtros
        - 401 Unauthorized: No autenticado
        - 500 Internal Server Error: Error del servidor
        """
        try:
            # Extraer query params
            routine_id = None
            if request.query_params.get("routineId"):
                try:
                    routine_id = int(request.query_params.get("routineId"))
                except (ValueError, TypeError):
                    return Response(
                        {
                            "error": "Validation error",
                            "message": {"routineId": "Debe ser un número entero"},
                            "request": {
                                "method": request.method,
                                "path": request.path,
                                "host": request.get_host(),
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            date_filter = None
            if request.query_params.get("date"):
                try:
                    from datetime import datetime
                    date_filter = datetime.strptime(
                        request.query_params.get("date"), "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return Response(
                        {
                            "error": "Validation error",
                            "message": {"date": "Formato inválido. Use YYYY-MM-DD"},
                            "request": {
                                "method": request.method,
                                "path": request.path,
                                "host": request.get_host(),
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Llamar al servicio
            sessions = list_sessions_service(
                user=request.user,
                routine_id=routine_id,
                date_filter=date_filter,
            )

            # Serializar datos
            serializer = SessionSerializer(sessions, many=True)

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

    def post(self, request: "Request") -> Response:
        """
        Crea una nueva sesión (requiere autenticación).

        Body Parameters:
        - date (date, requerido): Fecha de la sesión
        - routineId (int, opcional): ID de la rutina a la que vincular
        - startTime (datetime, opcional): Hora de inicio
        - endTime (datetime, opcional): Hora de finalización
        - durationMinutes (int, opcional): Duración en minutos
        - notes (str, opcional): Notas generales
        - rpe (int, opcional): Rate of Perceived Exertion (1-10)
        - energyLevel (str, opcional): Nivel de energía
        - sleepHours (decimal, opcional): Horas de sueño

        Respuestas:
        - 201 Created: Sesión creada correctamente
        - 400 Bad Request: Error de validación
        - 401 Unauthorized: No autenticado
        - 500 Internal Server Error: Error del servidor
        """
        serializer = SessionCreateSerializer(data=request.data)

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
            session = create_session_service(
                validated_data=serializer.validated_data, user=request.user
            )

            # Serializar respuesta
            response_serializer = SessionSerializer(session)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Sesión creada correctamente",
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


class SessionDetailAPIView(APIView):
    """
    Endpoint para obtener, actualizar y eliminar una sesión específica.

    Endpoints:
    - GET /api/sessions/{id}/ - Obtiene detalle de una sesión (requiere autenticación + ser propietario)
    - PUT /api/sessions/{id}/ - Actualiza una sesión (requiere autenticación + ser propietario)
    - DELETE /api/sessions/{id}/ - Elimina una sesión (requiere autenticación + ser propietario)

    Permisos:
    - Todos los métodos: Requiere autenticación + ser el propietario de la sesión
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: "Request", pk: int) -> Response:
        """
        Obtiene el detalle completo de una sesión con ejercicios asociados.

        Path Parameters:
        - pk (int): ID de la sesión

        Respuestas:
        - 200 OK: Detalle de la sesión con ejercicios
        - 403 Forbidden: No eres el propietario de la sesión
        - 404 Not Found: Sesión no encontrada
        - 500 Internal Server Error: Error del servidor
        """
        try:
            # Llamar al servicio
            session = get_session_full_service(session_id=pk, user=request.user)

            # Serializar respuesta
            serializer = SessionFullSerializer(session)

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
                    "message": "Sesión no encontrada",
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
                    "message": "Solo puedes ver tus propias sesiones",
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

    def put(self, request: "Request", pk: int) -> Response:
        """
        Actualiza una sesión existente (requiere autenticación y ser el propietario).

        Path Parameters:
        - pk (int): ID de la sesión a actualizar

        Body Parameters:
        Todos los campos son opcionales (solo se actualizan los proporcionados).

        Respuestas:
        - 200 OK: Sesión actualizada correctamente
        - 400 Bad Request: Error de validación
        - 403 Forbidden: No eres el propietario de la sesión
        - 404 Not Found: Sesión no encontrada
        - 500 Internal Server Error: Error del servidor
        """
        serializer = SessionUpdateSerializer(data=request.data)

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
            session = update_session_service(
                session_id=pk,
                validated_data=serializer.validated_data,
                user=request.user,
            )

            # Serializar respuesta
            response_serializer = SessionSerializer(session)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Sesión actualizada correctamente",
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
                    "message": "Sesión no encontrada",
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
                    "message": "Solo puedes actualizar tus propias sesiones",
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

    def delete(self, request: "Request", pk: int) -> Response:
        """
        Elimina una sesión (requiere autenticación y ser el propietario).

        Path Parameters:
        - pk (int): ID de la sesión a eliminar

        Respuestas:
        - 204 No Content: Sesión eliminada correctamente
        - 403 Forbidden: No eres el propietario de la sesión
        - 404 Not Found: Sesión no encontrada
        - 500 Internal Server Error: Error del servidor
        """
        try:
            # Llamar al servicio
            delete_session_service(session_id=pk, user=request.user)

            return Response(
                {
                    "message": "Sesión eliminada correctamente",
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
                    "message": "Sesión no encontrada",
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
                    "message": "Solo puedes eliminar tus propias sesiones",
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


class SessionExerciseListAPIView(APIView):
    """
    Endpoint para listar y crear ejercicios de una sesión.

    Endpoints:
    - GET /api/sessions/{sessionId}/exercises/ - Lista ejercicios de una sesión
    - POST /api/sessions/{sessionId}/exercises/ - Añade un ejercicio a una sesión

    Permisos:
    - Todos los métodos: Requiere autenticación + ser el propietario de la sesión
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: "Request", sessionId: int) -> Response:
        """
        Lista ejercicios de una sesión.

        Path Parameters:
        - sessionId (int): ID de la sesión

        Respuestas:
        - 200 OK: Lista de ejercicios
        - 403 Forbidden: No eres el propietario de la sesión
        - 404 Not Found: Sesión no encontrada
        - 500 Internal Server Error: Error del servidor
        """
        try:
            # Llamar al servicio
            exercises = list_session_exercises_service(
                session_id=sessionId, user=request.user
            )

            # Serializar datos
            serializer = SessionExerciseSerializer(exercises, many=True)

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
                    "message": "Sesión no encontrada",
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
                    "message": "Solo puedes ver ejercicios de tus propias sesiones",
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

    def post(self, request: "Request", sessionId: int) -> Response:
        """
        Añade un ejercicio a una sesión.

        Path Parameters:
        - sessionId (int): ID de la sesión

        Body Parameters:
        - exerciseId (int, requerido): ID del ejercicio
        - order (int, opcional): Orden del ejercicio
        - setsCompleted (int, opcional): Series completadas
        - repetitions (str, opcional): Repeticiones
        - weight (decimal, opcional): Peso en kilogramos
        - rpe (int, opcional): RPE (1-10)
        - restSeconds (int, opcional): Tiempo de descanso
        - notes (str, opcional): Notas

        Respuestas:
        - 201 Created: Ejercicio añadido correctamente
        - 400 Bad Request: Error de validación
        - 403 Forbidden: No eres el propietario de la sesión
        - 404 Not Found: Sesión o ejercicio no encontrado
        - 500 Internal Server Error: Error del servidor
        """
        serializer = SessionExerciseCreateSerializer(data=request.data)

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
            session_exercise = create_session_exercise_service(
                session_id=sessionId,
                validated_data=serializer.validated_data,
                user=request.user,
            )

            # Serializar respuesta
            response_serializer = SessionExerciseSerializer(session_exercise)

            return Response(
                {
                    "data": response_serializer.data,
                    "message": "Ejercicio añadido a la sesión correctamente",
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
                    "message": "Sesión o ejercicio no encontrado",
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
                    "message": "Solo puedes añadir ejercicios a tus propias sesiones",
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


class SessionExerciseDetailAPIView(APIView):
    """
    Endpoint para obtener, actualizar y eliminar un ejercicio de sesión específico.

    Endpoints:
    - GET /api/sessions/{sessionId}/exercises/{id}/ - Obtiene detalle de un ejercicio
    - PUT /api/sessions/{sessionId}/exercises/{id}/ - Actualiza un ejercicio
    - DELETE /api/sessions/{sessionId}/exercises/{id}/ - Elimina un ejercicio

    Permisos:
    - Todos los métodos: Requiere autenticación + ser el propietario de la sesión
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: "Request", sessionId: int, pk: int) -> Response:
        """
        Obtiene el detalle de un ejercicio de sesión.

        Path Parameters:
        - sessionId (int): ID de la sesión
        - pk (int): ID del ejercicio de sesión

        Respuestas:
        - 200 OK: Detalle del ejercicio
        - 403 Forbidden: No eres el propietario de la sesión
        - 404 Not Found: Ejercicio no encontrado
        - 500 Internal Server Error: Error del servidor
        """
        try:
            # Llamar al servicio
            session_exercise = get_session_exercise_service(
                session_exercise_id=pk, user=request.user
            )

            # Verificar que pertenece a la sesión correcta
            if session_exercise.session.id != sessionId:
                return Response(
                    {
                        "error": "Not found",
                        "message": "Ejercicio no encontrado en esta sesión",
                        "request": {
                            "method": request.method,
                            "path": request.path,
                            "host": request.get_host(),
                        },
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Serializar respuesta
            serializer = SessionExerciseSerializer(session_exercise)

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
        except PermissionDenied:
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Solo puedes ver ejercicios de tus propias sesiones",
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

    def put(self, request: "Request", sessionId: int, pk: int) -> Response:
        """
        Actualiza un ejercicio de sesión existente.

        Path Parameters:
        - sessionId (int): ID de la sesión
        - pk (int): ID del ejercicio a actualizar

        Body Parameters:
        Todos los campos son opcionales.

        Respuestas:
        - 200 OK: Ejercicio actualizado correctamente
        - 400 Bad Request: Error de validación
        - 403 Forbidden: No eres el propietario de la sesión
        - 404 Not Found: Ejercicio no encontrado
        - 500 Internal Server Error: Error del servidor
        """
        serializer = SessionExerciseUpdateSerializer(data=request.data)

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
            # Verificar que el ejercicio pertenece a la sesión
            session_exercise = get_session_exercise_service(
                session_exercise_id=pk, user=request.user
            )
            if session_exercise.session.id != sessionId:
                return Response(
                    {
                        "error": "Not found",
                        "message": "Ejercicio no encontrado en esta sesión",
                        "request": {
                            "method": request.method,
                            "path": request.path,
                            "host": request.get_host(),
                        },
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Llamar al servicio
            updated_exercise = update_session_exercise_service(
                session_exercise_id=pk,
                validated_data=serializer.validated_data,
                user=request.user,
            )

            # Serializar respuesta
            response_serializer = SessionExerciseSerializer(updated_exercise)

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
                    "message": "Solo puedes actualizar ejercicios de tus propias sesiones",
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

    def delete(self, request: "Request", sessionId: int, pk: int) -> Response:
        """
        Elimina un ejercicio de sesión.

        Path Parameters:
        - sessionId (int): ID de la sesión
        - pk (int): ID del ejercicio a eliminar

        Respuestas:
        - 204 No Content: Ejercicio eliminado correctamente
        - 403 Forbidden: No eres el propietario de la sesión
        - 404 Not Found: Ejercicio no encontrado
        - 500 Internal Server Error: Error del servidor
        """
        try:
            # Verificar que el ejercicio pertenece a la sesión
            session_exercise = get_session_exercise_service(
                session_exercise_id=pk, user=request.user
            )
            if session_exercise.session.id != sessionId:
                return Response(
                    {
                        "error": "Not found",
                        "message": "Ejercicio no encontrado en esta sesión",
                        "request": {
                            "method": request.method,
                            "path": request.path,
                            "host": request.get_host(),
                        },
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Llamar al servicio
            delete_session_exercise_service(session_exercise_id=pk, user=request.user)

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
                    "message": "Solo puedes eliminar ejercicios de tus propias sesiones",
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

