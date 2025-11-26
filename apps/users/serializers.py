from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework import serializers

from apps.users.models import User
from apps.users.repositories import get_user_by_username_repository, get_user_by_email_repository

if TYPE_CHECKING:
    pass


class UserRegisterSerializer(serializers.Serializer):
    """Serializer para registro de usuarios."""

    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    firstName = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    lastName = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    dateOfBirth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, required=False, allow_null=True)
    height = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)

    def validate_username(self, value: str) -> str:
        """Valida que el username sea único."""
        if get_user_by_username_repository(username=value):
            raise serializers.ValidationError("Este username ya está en uso.")
        return value

    def validate_email(self, value: str) -> str:
        """Valida que el email sea único."""
        if get_user_by_email_repository(email=value):
            raise serializers.ValidationError("Este email ya está en uso.")
        return value


class UserLoginSerializer(serializers.Serializer):
    """Serializer para inicio de sesión."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para el perfil del usuario."""

    firstName = serializers.CharField(source="first_name", read_only=True)
    lastName = serializers.CharField(source="last_name", read_only=True)
    dateOfBirth = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    isActive = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "firstName",
            "lastName",
            "dateOfBirth",
            "gender",
            "height",
            "weight",
            "isActive",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "username", "email", "createdAt", "updatedAt", "isActive"]

    def get_dateOfBirth(self, obj: User) -> str | None:
        """Retorna dateOfBirth en formato ISO."""
        return obj.dateOfBirth


class UserUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar el perfil del usuario."""

    firstName = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    lastName = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    dateOfBirth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, required=False, allow_null=True)
    height = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)

