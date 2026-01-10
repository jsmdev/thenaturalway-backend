from __future__ import annotations

from typing import ClassVar

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class MuscleGroup(models.Model):
    """Modelo para grupos musculares configurables con soporte jerárquico."""

    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subgroups",
        db_index=True,
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "muscle_groups"
        verbose_name = "Muscle Group"
        verbose_name_plural = "Muscle Groups"
        ordering: ClassVar[list[str]] = ["order", "name"]
        indexes: ClassVar[list] = [
            models.Index(fields=["name"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent.display_name} > {self.display_name}"
        return self.display_name

    def clean(self) -> None:
        """Validar que no haya referencias circulares o auto-referencias."""
        super().clean()

        # Prevenir auto-referencias
        if self.pk and self.parent_id == self.pk:
            raise ValidationError("Un grupo muscular no puede ser su propio padre.")

        # Prevenir referencias circulares
        if self.parent_id:
            visited = set()
            current = self.parent

            while current:
                if current.id == self.pk:
                    raise ValidationError(
                        "No se puede crear una referencia circular: "
                        "el padre no puede ser descendiente de este grupo."
                    )
                if current.id in visited:
                    break
                visited.add(current.id)
                current = current.parent


class MovementType(models.Model):
    """Modelo para tipos de movimiento configurables."""

    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "movement_types"
        verbose_name = "Movement Type"
        verbose_name_plural = "Movement Types"
        ordering: ClassVar[list[str]] = ["order", "name"]
        indexes: ClassVar[list] = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self) -> str:
        return self.display_name


class Equipment(models.Model):
    """Modelo para equipamiento configurable."""

    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "equipment"
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"
        ordering: ClassVar[list[str]] = ["order", "name"]
        indexes: ClassVar[list] = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self) -> str:
        return self.display_name


class Difficulty(models.Model):
    """Modelo para niveles de dificultad configurables."""

    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "difficulties"
        verbose_name = "Difficulty"
        verbose_name_plural = "Difficulties"
        ordering: ClassVar[list[str]] = ["order", "name"]
        indexes: ClassVar[list] = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self) -> str:
        return self.display_name


class Exercise(models.Model):
    """Modelo de ejercicio según el dominio."""

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    movement_type = models.ForeignKey(
        MovementType, on_delete=models.SET_NULL, null=True, blank=True, related_name="exercises"
    )
    primary_muscle_group = models.ForeignKey(
        MuscleGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exercises",
        db_index=True,
    )
    secondary_muscle_groups = models.JSONField(default=list, blank=True)
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exercises",
        db_index=True,
    )
    difficulty = models.ForeignKey(
        Difficulty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exercises",
        db_index=True,
    )
    instructions = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="exercises"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exercises"
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"
        indexes: ClassVar[list] = [
            models.Index(fields=["name"]),
            models.Index(fields=["primary_muscle_group"]),
            models.Index(fields=["equipment"]),
            models.Index(fields=["difficulty"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name
