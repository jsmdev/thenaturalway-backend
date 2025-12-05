from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from rest_framework.exceptions import ValidationError

from apps.users.repositories import (
    create_user_repository,
    get_user_by_email_repository,
    get_user_by_username_repository,
    update_user_repository,
)

if TYPE_CHECKING:
    from apps.users.models import User


def register_user_service(
    username: str,
    email: str,
    password: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
) -> User:
    """Servicio para registrar un nuevo usuario."""
    # Validar unicidad de username
    if get_user_by_username_repository(username=username):
        raise ValidationError({"username": "Este username ya está en uso."})

    # Validar unicidad de email
    if get_user_by_email_repository(email=email):
        raise ValidationError({"email": "Este email ya está en uso."})

    # Validar password
    if not password or len(password) < 8:
        raise ValidationError({"password": "La contraseña debe tener al menos 8 caracteres."})

    # Crear usuario
    user = create_user_repository(
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

    return user


def authenticate_user_service(username: str, password: str) -> Optional[User]:
    """Servicio para autenticar un usuario."""
    user = get_user_by_username_repository(username=username)

    if not user:
        return None

    if not user.check_password(password):
        return None

    if not user.is_active:
        return None

    return user


def get_user_profile_service(user: User) -> dict[str, Any]:
    """Servicio para obtener el perfil de un usuario."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "dateOfBirth": user.dateOfBirth,
        "gender": user.gender,
        "height": float(user.height) if user.height else None,
        "weight": float(user.weight) if user.weight else None,
        "isActive": user.is_active,
        "createdAt": user.created_at.isoformat(),
        "updatedAt": user.updated_at.isoformat(),
    }


def update_user_profile_service(
    user: User,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
) -> User:
    """Servicio para actualizar el perfil de un usuario."""
    # Validar gender si se proporciona
    if gender is not None:
        valid_genders = ["male", "female", "other"]
        if gender not in valid_genders:
            raise ValidationError(
                {"gender": f"El género debe ser uno de: {', '.join(valid_genders)}"}
            )

    # Actualizar usuario
    updated_user = update_user_repository(
        user=user,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        gender=gender,
        height=height,
        weight=weight,
    )

    return updated_user
