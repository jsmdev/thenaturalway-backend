from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exercises.serializers import (
    ExerciseCreateSerializer,
    ExerciseSerializer,
    ExerciseUpdateSerializer,
)
from apps.exercises.services import (
    create_exercise_service,
    delete_exercise_service,
    get_exercise_service,
    list_exercises_service,
    update_exercise_service,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


class ExerciseListAPIView(APIView):
    """
    Endpoint para listar y crear ejercicios.

    **Endpoints:**
    - `GET /api/exercises/` - Lista ejercicios con filtros y búsqueda (público)
    - `POST /api/exercises/` - Crea un nuevo ejercicio (requiere autenticación)

    **Permisos:**
    - GET: Público (AllowAny)
    - POST: Requiere autenticación (IsAuthenticated)

    **Ejemplo de uso:**
    ```python
    # GET /api/exercises/?primaryMuscleGroup=chest&equipment=barbell&search=bench
    # POST /api/exercises/ con body JSON
    ```
    """

    def get_permissions(self):
        """
        Permisos diferentes según el método HTTP.

        Returns:
            Lista de clases de permisos según el método HTTP.
        """
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request: Request) -> Response:
        """
        Lista ejercicios con filtros y búsqueda.

        **Query Parameters:**
        - `primaryMuscleGroup` (str, opcional): Filtra por grupo muscular principal
          - Valores válidos: chest, back, shoulders, arms, legs, core, full_body, other
        - `equipment` (str, opcional): Filtra por equipamiento
          - Valores válidos: barbell, dumbbell, cable, machine, bodyweight, kettlebell, other
        - `difficulty` (str, opcional): Filtra por dificultad
          - Valores válidos: beginner, intermediate, advanced
        - `isActive` (bool, opcional): Filtra por estado activo/inactivo
          - Valores: true, false, 1, 0, yes, no
        - `createdBy` (int, opcional): Filtra por ID de usuario creador
        - `search` (str, opcional): Búsqueda por texto en nombre y descripción
        - `ordering` (str, opcional): Campo para ordenamiento (por defecto: name)

        **Respuestas:**
        - 200 OK: Lista de ejercicios
        - 400 Bad Request: Error de validación en filtros
        - 500 Internal Server Error: Error del servidor

        **Ejemplo de respuesta exitosa:**
        ```json
        {
          "data": [
            {
              "id": 1,
              "name": "Bench Press",
              "description": "...",
              "primaryMuscleGroup": "chest",
              ...
            }
          ],
          "request": {
            "method": "GET",
            "path": "/api/exercises/",
            "host": "example.com"
          }
        }
        ```

        Args:
            request: Request HTTP con query parameters opcionales

        Returns:
            Response con lista de ejercicios serializados
        """
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
        """
        Crea un nuevo ejercicio (requiere autenticación).

        **Permisos:**
        - Requiere autenticación (IsAuthenticated)
        - El usuario autenticado se asigna como creador del ejercicio

        **Body Parameters:**
        - `name` (str, requerido): Nombre del ejercicio (máx. 255 caracteres)
        - `description` (str, opcional): Descripción del ejercicio
        - `movementType` (str, opcional): Tipo de movimiento
          - Valores válidos: push, pull, squat, hinge, carry, other
        - `primaryMuscleGroup` (str, opcional): Grupo muscular principal
          - Valores válidos: chest, back, shoulders, arms, legs, core, full_body, other
        - `secondaryMuscleGroups` (array[str], opcional): Grupos musculares secundarios
          - Cada elemento debe ser uno de los valores válidos de primaryMuscleGroup
        - `equipment` (str, opcional): Equipamiento necesario
          - Valores válidos: barbell, dumbbell, cable, machine, bodyweight, kettlebell, other
        - `difficulty` (str, opcional): Nivel de dificultad
          - Valores válidos: beginner, intermediate, advanced
        - `instructions` (str, opcional): Instrucciones de ejecución
        - `imageUrl` (str, opcional): URL de imagen del ejercicio
        - `videoUrl` (str, opcional): URL de video del ejercicio
        - `isActive` (bool, opcional): Estado activo (por defecto: true)

        **Respuestas:**
        - 201 Created: Ejercicio creado correctamente
        - 400 Bad Request: Error de validación
        - 401 Unauthorized: No autenticado
        - 500 Internal Server Error: Error del servidor

        **Ejemplo de request:**
        ```json
        {
          "name": "Bench Press",
          "description": "Press de banca con barra",
          "primaryMuscleGroup": "chest",
          "equipment": "barbell",
          "difficulty": "intermediate"
        }
        ```

        **Ejemplo de respuesta exitosa:**
        ```json
        {
          "data": {
            "id": 1,
            "name": "Bench Press",
            ...
          },
          "message": "Ejercicio creado correctamente",
          "request": {...}
        }
        ```

        Args:
            request: Request HTTP con datos del ejercicio en el body

        Returns:
            Response con el ejercicio creado serializado
        """
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
    """
    Endpoint para obtener, actualizar y eliminar un ejercicio específico.

    **Endpoints:**
    - `GET /api/exercises/{id}/` - Obtiene detalle de un ejercicio (público)
    - `PUT /api/exercises/{id}/` - Actualiza un ejercicio (requiere autenticación + ser creador)
    - `DELETE /api/exercises/{id}/` - Elimina un ejercicio (soft delete, requiere autenticación + ser creador)

    **Permisos:**
    - GET: Público (AllowAny)
    - PUT: Requiere autenticación + ser el creador del ejercicio
    - DELETE: Requiere autenticación + ser el creador del ejercicio
    """

    def get_permissions(self):
        """
        Permisos diferentes según el método HTTP.

        Returns:
            Lista de clases de permisos según el método HTTP.
        """
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request: Request, pk: int) -> Response:
        """
        Obtiene el detalle de un ejercicio.

        **Path Parameters:**
        - `pk` (int): ID del ejercicio

        **Respuestas:**
        - 200 OK: Detalle del ejercicio
        - 404 Not Found: Ejercicio no encontrado
        - 500 Internal Server Error: Error del servidor

        **Ejemplo de respuesta exitosa:**
        ```json
        {
          "data": {
            "id": 1,
            "name": "Bench Press",
            "description": "...",
            "primaryMuscleGroup": "chest",
            ...
          },
          "request": {...}
        }
        ```

        Args:
            request: Request HTTP
            pk: ID del ejercicio

        Returns:
            Response con el detalle del ejercicio serializado
        """
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
        """
        Actualiza un ejercicio existente (requiere autenticación y ser el creador).

        **Permisos:**
        - Requiere autenticación (IsAuthenticated)
        - Solo el creador del ejercicio puede actualizarlo

        **Path Parameters:**
        - `pk` (int): ID del ejercicio a actualizar

        **Body Parameters:**
        Todos los campos son opcionales (solo se actualizan los proporcionados):
        - `name` (str, opcional): Nombre del ejercicio
        - `description` (str, opcional): Descripción
        - `movementType` (str, opcional): Tipo de movimiento
        - `primaryMuscleGroup` (str, opcional): Grupo muscular principal
        - `secondaryMuscleGroups` (array[str], opcional): Grupos musculares secundarios
        - `equipment` (str, opcional): Equipamiento
        - `difficulty` (str, opcional): Dificultad
        - `instructions` (str, opcional): Instrucciones
        - `imageUrl` (str, opcional): URL de imagen
        - `videoUrl` (str, opcional): URL de video
        - `isActive` (bool, opcional): Estado activo

        **Respuestas:**
        - 200 OK: Ejercicio actualizado correctamente
        - 400 Bad Request: Error de validación
        - 401 Unauthorized: No autenticado
        - 403 Forbidden: No eres el creador del ejercicio
        - 404 Not Found: Ejercicio no encontrado
        - 500 Internal Server Error: Error del servidor

        Args:
            request: Request HTTP con datos a actualizar en el body
            pk: ID del ejercicio a actualizar

        Returns:
            Response con el ejercicio actualizado serializado
        """
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
        """
        Elimina un ejercicio (soft delete, requiere autenticación y ser el creador).

        **Permisos:**
        - Requiere autenticación (IsAuthenticated)
        - Solo el creador del ejercicio puede eliminarlo

        **Path Parameters:**
        - `pk` (int): ID del ejercicio a eliminar

        **Nota:**
        La eliminación es "soft delete": se marca `isActive=False` pero el registro
        permanece en la base de datos. Esto permite recuperación de datos si es necesario.

        **Respuestas:**
        - 204 No Content: Ejercicio eliminado correctamente
        - 401 Unauthorized: No autenticado
        - 403 Forbidden: No eres el creador del ejercicio
        - 404 Not Found: Ejercicio no encontrado
        - 500 Internal Server Error: Error del servidor

        Args:
            request: Request HTTP
            pk: ID del ejercicio a eliminar

        Returns:
            Response vacío con código 204 No Content
        """
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
