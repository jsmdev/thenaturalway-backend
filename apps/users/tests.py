from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.users.models import User
from apps.users.repositories import (
    get_user_by_id_repository,
    get_user_by_username_repository,
    get_user_by_email_repository,
    create_user_repository,
    update_user_repository,
)
from apps.users.services import (
    register_user_service,
    authenticate_user_service,
    get_user_profile_service,
    update_user_profile_service,
)
from apps.users.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)

if TYPE_CHECKING:
    pass

UserModel = get_user_model()


# ============================================================================
# Tests de Repositorios
# ============================================================================


class UserRepositoryTestCase(TestCase):
    """Tests unitarios para repositorios de usuarios."""

    def setUp(self) -> None:
        """Configuración inicial para cada test."""
        # Arrange: Crear usuario de prueba
        self.test_user = UserModel.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_get_user_by_id_repository_should_return_user_when_exists(self) -> None:
        """Test: Debe retornar usuario cuando existe por ID."""
        # Arrange
        user_id = self.test_user.id

        # Act
        result = get_user_by_id_repository(user_id=user_id)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, user_id)
        self.assertEqual(result.username, "testuser")

    def test_get_user_by_id_repository_should_return_none_when_not_exists(self) -> None:
        """Test: Debe retornar None cuando el usuario no existe por ID."""
        # Arrange
        non_existent_id = 99999

        # Act
        result = get_user_by_id_repository(user_id=non_existent_id)

        # Assert
        self.assertIsNone(result)

    def test_get_user_by_username_repository_should_return_user_when_exists(self) -> None:
        """Test: Debe retornar usuario cuando existe por username."""
        # Arrange
        username = "testuser"

        # Act
        result = get_user_by_username_repository(username=username)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, username)

    def test_get_user_by_username_repository_should_return_none_when_not_exists(self) -> None:
        """Test: Debe retornar None cuando el usuario no existe por username."""
        # Arrange
        non_existent_username = "nonexistent"

        # Act
        result = get_user_by_username_repository(username=non_existent_username)

        # Assert
        self.assertIsNone(result)

    def test_get_user_by_email_repository_should_return_user_when_exists(self) -> None:
        """Test: Debe retornar usuario cuando existe por email."""
        # Arrange
        email = "test@example.com"

        # Act
        result = get_user_by_email_repository(email=email)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.email, email)

    def test_get_user_by_email_repository_should_return_none_when_not_exists(self) -> None:
        """Test: Debe retornar None cuando el usuario no existe por email."""
        # Arrange
        non_existent_email = "nonexistent@example.com"

        # Act
        result = get_user_by_email_repository(email=non_existent_email)

        # Assert
        self.assertIsNone(result)

    def test_create_user_repository_should_create_user_with_required_fields(self) -> None:
        """Test: Debe crear usuario con campos requeridos."""
        # Arrange
        username = "newuser"
        email = "newuser@example.com"
        password = "newpass123"

        # Act
        result = create_user_repository(
            username=username,
            email=email,
            password=password,
        )

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, username)
        self.assertEqual(result.email, email)
        self.assertTrue(result.check_password(password))
        self.assertTrue(result.is_active)

    def test_create_user_repository_should_create_user_with_optional_fields(self) -> None:
        """Test: Debe crear usuario con campos opcionales."""
        # Arrange
        username = "newuser2"
        email = "newuser2@example.com"
        password = "newpass123"
        first_name = "New"
        last_name = "User"
        date_of_birth = "1990-01-01"
        gender = "male"
        height = Decimal("175.50")
        weight = Decimal("70.00")

        # Act
        result = create_user_repository(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            height=height,
            weight=weight,
        )

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.first_name, first_name)
        self.assertEqual(result.last_name, last_name)
        self.assertEqual(result.date_of_birth, date(1990, 1, 1))
        self.assertEqual(result.gender, gender)
        self.assertEqual(result.height, height)
        self.assertEqual(result.weight, weight)

    def test_update_user_repository_should_update_user_fields(self) -> None:
        """Test: Debe actualizar campos del usuario."""
        # Arrange
        new_first_name = "Updated"
        new_last_name = "Name"
        new_date_of_birth = "1995-05-15"
        new_gender = "female"
        new_height = Decimal("180.00")
        new_weight = Decimal("75.00")

        # Act
        result = update_user_repository(
            user=self.test_user,
            first_name=new_first_name,
            last_name=new_last_name,
            date_of_birth=new_date_of_birth,
            gender=new_gender,
            height=new_height,
            weight=new_weight,
        )

        # Assert
        self.assertEqual(result.first_name, new_first_name)
        self.assertEqual(result.last_name, new_last_name)
        self.assertEqual(result.date_of_birth, date(1995, 5, 15))
        self.assertEqual(result.gender, new_gender)
        self.assertEqual(result.height, new_height)
        self.assertEqual(result.weight, new_weight)

    def test_update_user_repository_should_update_partial_fields(self) -> None:
        """Test: Debe actualizar solo campos proporcionados."""
        # Arrange
        original_first_name = self.test_user.first_name
        new_last_name = "UpdatedLastName"

        # Act
        result = update_user_repository(
            user=self.test_user,
            last_name=new_last_name,
        )

        # Assert
        self.assertEqual(result.first_name, original_first_name)
        self.assertEqual(result.last_name, new_last_name)


# ============================================================================
# Tests de Servicios
# ============================================================================


class UserServiceTestCase(TestCase):
    """Tests unitarios para servicios de usuarios."""

    def setUp(self) -> None:
        """Configuración inicial para cada test."""
        # Arrange: Crear usuario de prueba
        self.test_user = UserModel.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_register_user_service_should_create_user_with_valid_data(self) -> None:
        """Test: Debe crear usuario con datos válidos."""
        # Arrange
        username = "newuser"
        email = "newuser@example.com"
        password = "validpass123"

        # Act
        result = register_user_service(
            username=username,
            email=email,
            password=password,
        )

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, username)
        self.assertEqual(result.email, email)
        self.assertTrue(result.check_password(password))

    def test_register_user_service_should_raise_error_when_username_exists(self) -> None:
        """Test: Debe lanzar error cuando el username ya existe."""
        # Arrange
        username = "testuser"  # Ya existe
        email = "newemail@example.com"
        password = "validpass123"

        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            register_user_service(
                username=username,
                email=email,
                password=password,
            )

        self.assertIn("username", str(context.exception))

    def test_register_user_service_should_raise_error_when_email_exists(self) -> None:
        """Test: Debe lanzar error cuando el email ya existe."""
        # Arrange
        username = "newuser"
        email = "test@example.com"  # Ya existe
        password = "validpass123"

        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            register_user_service(
                username=username,
                email=email,
                password=password,
            )

        self.assertIn("email", str(context.exception))

    def test_register_user_service_should_raise_error_when_password_too_short(self) -> None:
        """Test: Debe lanzar error cuando la contraseña es muy corta."""
        # Arrange
        username = "newuser"
        email = "newuser@example.com"
        password = "short"  # Menos de 8 caracteres

        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            register_user_service(
                username=username,
                email=email,
                password=password,
            )

        self.assertIn("password", str(context.exception))

    def test_authenticate_user_service_should_return_user_with_valid_credentials(self) -> None:
        """Test: Debe retornar usuario con credenciales válidas."""
        # Arrange
        username = "testuser"
        password = "testpass123"

        # Act
        result = authenticate_user_service(username=username, password=password)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, username)

    def test_authenticate_user_service_should_return_none_with_invalid_username(self) -> None:
        """Test: Debe retornar None con username inválido."""
        # Arrange
        username = "nonexistent"
        password = "testpass123"

        # Act
        result = authenticate_user_service(username=username, password=password)

        # Assert
        self.assertIsNone(result)

    def test_authenticate_user_service_should_return_none_with_invalid_password(self) -> None:
        """Test: Debe retornar None con contraseña inválida."""
        # Arrange
        username = "testuser"
        password = "wrongpassword"

        # Act
        result = authenticate_user_service(username=username, password=password)

        # Assert
        self.assertIsNone(result)

    def test_authenticate_user_service_should_return_none_when_user_inactive(self) -> None:
        """Test: Debe retornar None cuando el usuario está inactivo."""
        # Arrange
        self.test_user.is_active = False
        self.test_user.save()
        username = "testuser"
        password = "testpass123"

        # Act
        result = authenticate_user_service(username=username, password=password)

        # Assert
        self.assertIsNone(result)

    def test_get_user_profile_service_should_return_complete_profile_data(self) -> None:
        """Test: Debe retornar datos completos del perfil."""
        # Arrange
        user = self.test_user

        # Act
        result = get_user_profile_service(user=user)

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], user.id)
        self.assertEqual(result["username"], user.username)
        self.assertEqual(result["email"], user.email)
        self.assertEqual(result["firstName"], user.first_name)
        self.assertEqual(result["lastName"], user.last_name)
        self.assertIn("createdAt", result)
        self.assertIn("updatedAt", result)

    def test_update_user_profile_service_should_update_user_with_valid_data(self) -> None:
        """Test: Debe actualizar usuario con datos válidos."""
        # Arrange
        user = self.test_user
        new_first_name = "Updated"
        new_last_name = "Name"
        new_gender = "female"

        # Act
        result = update_user_profile_service(
            user=user,
            first_name=new_first_name,
            last_name=new_last_name,
            gender=new_gender,
        )

        # Assert
        self.assertEqual(result.first_name, new_first_name)
        self.assertEqual(result.last_name, new_last_name)
        self.assertEqual(result.gender, new_gender)

    def test_update_user_profile_service_should_raise_error_with_invalid_gender(self) -> None:
        """Test: Debe lanzar error con género inválido."""
        # Arrange
        user = self.test_user
        invalid_gender = "invalid_gender"

        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            update_user_profile_service(
                user=user,
                gender=invalid_gender,
            )

        self.assertIn("gender", str(context.exception))


# ============================================================================
# Tests de Serializadores
# ============================================================================


class UserSerializerTestCase(TestCase):
    """Tests unitarios para serializadores de usuarios."""

    def setUp(self) -> None:
        """Configuración inicial para cada test."""
        # Arrange: Crear usuario de prueba
        self.test_user = UserModel.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_user_register_serializer_should_validate_valid_data(self) -> None:
        """Test: Debe validar datos válidos de registro."""
        # Arrange
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "validpass123",
            "firstName": "New",
            "lastName": "User",
        }

        # Act
        serializer = UserRegisterSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())

    def test_user_register_serializer_should_reject_duplicate_username(self) -> None:
        """Test: Debe rechazar username duplicado."""
        # Arrange
        data = {
            "username": "testuser",  # Ya existe
            "email": "newemail@example.com",
            "password": "validpass123",
        }

        # Act
        serializer = UserRegisterSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_user_register_serializer_should_reject_duplicate_email(self) -> None:
        """Test: Debe rechazar email duplicado."""
        # Arrange
        data = {
            "username": "newuser",
            "email": "test@example.com",  # Ya existe
            "password": "validpass123",
        }

        # Act
        serializer = UserRegisterSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_user_register_serializer_should_reject_short_password(self) -> None:
        """Test: Debe rechazar contraseña muy corta."""
        # Arrange
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "short",  # Menos de 8 caracteres
        }

        # Act
        serializer = UserRegisterSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_user_login_serializer_should_validate_valid_data(self) -> None:
        """Test: Debe validar datos válidos de login."""
        # Arrange
        data = {
            "username": "testuser",
            "password": "testpass123",
        }

        # Act
        serializer = UserLoginSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())

    def test_user_profile_serializer_should_serialize_user_data(self) -> None:
        """Test: Debe serializar datos del usuario."""
        # Arrange
        user = self.test_user

        # Act
        serializer = UserProfileSerializer(user)

        # Assert
        self.assertEqual(serializer.data["id"], user.id)
        self.assertEqual(serializer.data["username"], user.username)
        self.assertEqual(serializer.data["email"], user.email)
        self.assertEqual(serializer.data["firstName"], user.first_name)
        self.assertEqual(serializer.data["lastName"], user.last_name)

    def test_user_update_serializer_should_validate_valid_data(self) -> None:
        """Test: Debe validar datos válidos de actualización."""
        # Arrange
        data = {
            "firstName": "Updated",
            "lastName": "Name",
            "gender": "female",
        }

        # Act
        serializer = UserUpdateSerializer(data=data)

        # Assert
        self.assertTrue(serializer.is_valid())

    def test_user_update_serializer_should_reject_invalid_gender(self) -> None:
        """Test: Debe rechazar género inválido."""
        # Arrange
        data = {
            "gender": "invalid_gender",
        }

        # Act
        serializer = UserUpdateSerializer(data=data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("gender", serializer.errors)


# ============================================================================
# Tests de Integración API
# ============================================================================


class UserAPITestCase(TestCase):
    """Tests de integración para endpoints de API de usuarios."""

    def setUp(self) -> None:
        """Configuración inicial para cada test."""
        # Arrange: Configurar cliente API
        self.client = APIClient()
        self.base_url = "/api/users/"

        # Crear usuario de prueba
        self.test_user = UserModel.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_register_endpoint_should_create_user_and_return_tokens(self) -> None:
        """Test: Debe crear usuario y retornar tokens JWT."""
        # Arrange
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "validpass123",
            "firstName": "New",
            "lastName": "User",
        }

        # Act
        response = self.client.post(f"{self.base_url}register/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertIn("user", response.data["data"])
        self.assertIn("tokens", response.data["data"])
        self.assertIn("access", response.data["data"]["tokens"])
        self.assertIn("refresh", response.data["data"]["tokens"])

    def test_register_endpoint_should_reject_duplicate_username(self) -> None:
        """Test: Debe rechazar registro con username duplicado."""
        # Arrange
        data = {
            "username": "testuser",  # Ya existe
            "email": "newemail@example.com",
            "password": "validpass123",
        }

        # Act
        response = self.client.post(f"{self.base_url}register/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_login_endpoint_should_return_tokens_with_valid_credentials(self) -> None:
        """Test: Debe retornar tokens con credenciales válidas."""
        # Arrange
        data = {
            "username": "testuser",
            "password": "testpass123",
        }

        # Act
        response = self.client.post(f"{self.base_url}login/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("tokens", response.data["data"])
        self.assertIn("access", response.data["data"]["tokens"])

    def test_login_endpoint_should_reject_invalid_credentials(self) -> None:
        """Test: Debe rechazar credenciales inválidas."""
        # Arrange
        data = {
            "username": "testuser",
            "password": "wrongpassword",
        }

        # Act
        response = self.client.post(f"{self.base_url}login/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_profile_get_endpoint_should_return_user_profile_when_authenticated(self) -> None:
        """Test: Debe retornar perfil cuando el usuario está autenticado."""
        # Arrange
        self.client.force_authenticate(user=self.test_user)

        # Act
        response = self.client.get(f"{self.base_url}me/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["username"], "testuser")

    def test_profile_get_endpoint_should_reject_when_not_authenticated(self) -> None:
        """Test: Debe rechazar cuando el usuario no está autenticado."""
        # Act
        response = self.client.get(f"{self.base_url}me/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_put_endpoint_should_update_user_profile_when_authenticated(self) -> None:
        """Test: Debe actualizar perfil cuando el usuario está autenticado."""
        # Arrange
        self.client.force_authenticate(user=self.test_user)
        data = {
            "firstName": "Updated",
            "lastName": "Name",
            "gender": "female",
        }

        # Act
        response = self.client.put(f"{self.base_url}me/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["firstName"], "Updated")
        self.assertEqual(response.data["data"]["lastName"], "Name")

    def test_profile_put_endpoint_should_reject_when_not_authenticated(self) -> None:
        """Test: Debe rechazar actualización cuando el usuario no está autenticado."""
        # Arrange
        data = {
            "firstName": "Updated",
        }

        # Act
        response = self.client.put(f"{self.base_url}me/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_endpoint_should_blacklist_token_when_authenticated(self) -> None:
        """Test: Debe invalidar token cuando el usuario está autenticado."""
        # Arrange
        self.client.force_authenticate(user=self.test_user)
        # Obtener refresh token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.test_user)
        data = {"refresh": str(refresh)}

        # Act
        response = self.client.post(f"{self.base_url}logout/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_logout_endpoint_should_reject_when_not_authenticated(self) -> None:
        """Test: Debe rechazar logout cuando el usuario no está autenticado."""
        # Act
        response = self.client.post(f"{self.base_url}logout/")

        # Assert
        # TokenBlacklistView retorna 403 cuando no hay autenticación
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_token_refresh_endpoint_should_return_new_access_token(self) -> None:
        """Test: Debe retornar nuevo access token con refresh token válido."""
        # Arrange
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.test_user)
        data = {"refresh": str(refresh)}

        # Act
        response = self.client.post(f"{self.base_url}refresh/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("access", response.data["data"])

    def test_token_refresh_endpoint_should_reject_invalid_refresh_token(self) -> None:
        """Test: Debe rechazar refresh token inválido."""
        # Arrange
        data = {"refresh": "invalid_token"}

        # Act
        response = self.client.post(f"{self.base_url}refresh/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
