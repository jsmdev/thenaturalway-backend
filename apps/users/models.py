from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

if TYPE_CHECKING:
    pass


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User."""

    def create_user(
        self, username: str, email: str, password: str | None = None, **extra_fields
    ) -> User:
        """Crea y retorna un usuario con email y password."""
        if not email:
            raise ValueError("El email es requerido")
        if not username:
            raise ValueError("El username es requerido")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username: str, email: str, password: str | None = None, **extra_fields
    ) -> User:
        """Crea y retorna un superusuario."""
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    """Modelo de usuario personalizado según el dominio."""

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        return self.username

    @property
    def firstName(self) -> str | None:
        """Alias para first_name (compatibilidad con dominio)."""
        return self.first_name

    @property
    def lastName(self) -> str | None:
        """Alias para last_name (compatibilidad con dominio)."""
        return self.last_name

    @property
    def dateOfBirth(self) -> str | None:
        """Alias para date_of_birth (compatibilidad con dominio)."""
        return self.date_of_birth.isoformat() if self.date_of_birth else None

