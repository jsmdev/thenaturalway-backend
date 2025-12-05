from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from apps.users.serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
)
from apps.users.services import (
    authenticate_user_service,
    get_user_profile_service,
    register_user_service,
    update_user_profile_service,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


class UserRegisterAPIView(APIView):
    """Endpoint para registro de nuevos usuarios."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Registra un nuevo usuario y retorna tokens JWT."""
        serializer = UserRegisterSerializer(data=request.data)

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
            user = register_user_service(
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data.get("firstName"),
                last_name=serializer.validated_data.get("lastName"),
                date_of_birth=serializer.validated_data.get("dateOfBirth"),
                gender=serializer.validated_data.get("gender"),
                height=serializer.validated_data.get("height"),
                weight=serializer.validated_data.get("weight"),
            )

            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "data": {
                        "user": UserProfileSerializer(user).data,
                        "tokens": {
                            "access": access_token,
                            "refresh": refresh_token,
                        },
                    },
                    "message": "Usuario registrado correctamente",
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_201_CREATED,
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


class UserLoginAPIView(APIView):
    """Endpoint para inicio de sesión."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Autentica un usuario y retorna tokens JWT."""
        serializer = UserLoginSerializer(data=request.data)

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
            user = authenticate_user_service(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )

            if not user:
                return Response(
                    {
                        "error": "Authentication failed",
                        "message": "Credenciales inválidas",
                        "request": {
                            "method": request.method,
                            "path": request.path,
                            "host": request.get_host(),
                        },
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "data": {
                        "user": UserProfileSerializer(user).data,
                        "tokens": {
                            "access": access_token,
                            "refresh": refresh_token,
                        },
                    },
                    "message": "Inicio de sesión exitoso",
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


class UserLogoutAPIView(TokenBlacklistView):
    """Endpoint para cerrar sesión."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Invalida el refresh token."""
        try:
            response = super().post(request)
            return Response(
                {
                    "message": "Sesión cerrada correctamente",
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


class UserProfileAPIView(APIView):
    """Endpoint para obtener y actualizar el perfil del usuario autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Retorna el perfil del usuario autenticado."""
        try:
            profile_data = get_user_profile_service(user=request.user)

            return Response(
                {
                    "data": profile_data,
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

    def put(self, request: Request) -> Response:
        """Actualiza el perfil del usuario autenticado."""
        serializer = UserUpdateSerializer(data=request.data)

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
            updated_user = update_user_profile_service(
                user=request.user,
                first_name=serializer.validated_data.get("firstName"),
                last_name=serializer.validated_data.get("lastName"),
                date_of_birth=serializer.validated_data.get("dateOfBirth"),
                gender=serializer.validated_data.get("gender"),
                height=serializer.validated_data.get("height"),
                weight=serializer.validated_data.get("weight"),
            )

            return Response(
                {
                    "data": UserProfileSerializer(updated_user).data,
                    "message": "Perfil actualizado correctamente",
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


class UserTokenRefreshAPIView(TokenRefreshView):
    """Endpoint para refrescar el access token."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Refresca el access token usando el refresh token."""
        try:
            response = super().post(request)
            return Response(
                {
                    "data": response.data,
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
                    "error": "Token refresh failed",
                    "message": str(error),
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "host": request.get_host(),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
