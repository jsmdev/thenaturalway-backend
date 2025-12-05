from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from apps.users.models import User

UserModel = get_user_model()


def get_user_by_id_repository(user_id: int) -> User | None:
    """Obtiene un usuario por su ID."""
    try:
        return UserModel.objects.get(id=user_id)
    except UserModel.DoesNotExist:
        return None


def get_user_by_username_repository(username: str) -> User | None:
    """Obtiene un usuario por su username."""
    try:
        return UserModel.objects.get(username=username)
    except UserModel.DoesNotExist:
        return None


def get_user_by_email_repository(email: str) -> User | None:
    """Obtiene un usuario por su email."""
    try:
        return UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        return None


def create_user_repository(
    username: str,
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: str | None = None,
    gender: str | None = None,
    height: float | None = None,
    weight: float | None = None,
) -> User:
    """Crea un nuevo usuario."""
    # Convertir date_of_birth de string a date si es necesario
    date_of_birth_obj = None
    if date_of_birth:
        if isinstance(date_of_birth, str):
            date_of_birth_obj = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        else:
            date_of_birth_obj = date_of_birth

    return UserModel.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth_obj,
        gender=gender,
        height=height,
        weight=weight,
    )


def update_user_repository(
    user: User,
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: str | None = None,
    gender: str | None = None,
    height: float | None = None,
    weight: float | None = None,
) -> User:
    """Actualiza los datos de un usuario."""
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if date_of_birth is not None:
        # Convertir date_of_birth de string a date si es necesario
        if isinstance(date_of_birth, str):
            user.date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        else:
            user.date_of_birth = date_of_birth
    if gender is not None:
        user.gender = gender
    if height is not None:
        user.height = height
    if weight is not None:
        user.weight = weight

    user.save()
    return user
