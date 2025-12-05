from __future__ import annotations

from typing import ClassVar

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Routine(models.Model):
    """Modelo de rutina según el dominio."""

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    duration_weeks = models.IntegerField(blank=True, null=True)
    duration_months = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="routines", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "routines"
        verbose_name = "Routine"
        verbose_name_plural = "Routines"
        indexes: ClassVar[list] = [
            models.Index(fields=["name"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


class Week(models.Model):
    """Modelo de semana dentro de una rutina."""

    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name="weeks", db_index=True
    )
    week_number = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "weeks"
        verbose_name = "Week"
        verbose_name_plural = "Weeks"
        unique_together: ClassVar[list[list[str]]] = [["routine", "week_number"]]
        indexes: ClassVar[list] = [
            models.Index(fields=["routine"]),
            models.Index(fields=["week_number"]),
        ]
        ordering: ClassVar[list[str]] = ["week_number"]

    def __str__(self) -> str:
        return f"Week {self.week_number} - {self.routine.name}"

    def save(self, *args, **kwargs) -> None:
        """Sobrescribe save para ejecutar validación."""
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Valida que week_number sea único por rutina."""
        if self.routine_id and self.week_number:
            existing = Week.objects.filter(
                routine=self.routine, week_number=self.week_number
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(
                    {"week_number": "Ya existe una semana con este número en esta rutina"}
                )


class Day(models.Model):
    """Modelo de día dentro de una semana."""

    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="days", db_index=True)
    day_number = models.IntegerField()
    name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "days"
        verbose_name = "Day"
        verbose_name_plural = "Days"
        unique_together: ClassVar[list[list[str]]] = [["week", "day_number"]]
        indexes: ClassVar[list] = [
            models.Index(fields=["week"]),
            models.Index(fields=["day_number"]),
        ]
        ordering: ClassVar[list[str]] = ["day_number"]

    def __str__(self) -> str:
        day_name = self.name or f"Día {self.day_number}"
        return f"{day_name} - {self.week}"

    def save(self, *args, **kwargs) -> None:
        """Sobrescribe save para ejecutar validación."""
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Valida que day_number sea único por semana."""
        if self.week_id and self.day_number:
            existing = Day.objects.filter(week=self.week, day_number=self.day_number).exclude(
                pk=self.pk
            )
            if existing.exists():
                raise ValidationError(
                    {"day_number": "Ya existe un día con este número en esta semana"}
                )


class Block(models.Model):
    """Modelo de bloque dentro de un día."""

    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="blocks", db_index=True)
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blocks"
        verbose_name = "Block"
        verbose_name_plural = "Blocks"
        indexes: ClassVar[list] = [
            models.Index(fields=["day"]),
            models.Index(fields=["order"]),
        ]
        ordering: ClassVar[list[str]] = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.name} - {self.day}"

    def save(self, *args, **kwargs) -> None:
        """Asigna order automáticamente si no se proporciona."""
        if not self.order and self.day_id:
            max_order = Block.objects.filter(day=self.day).aggregate(max_order=models.Max("order"))[
                "max_order"
            ]
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)


class RoutineExercise(models.Model):
    """Modelo de ejercicio dentro de un bloque de rutina."""

    block = models.ForeignKey(
        Block, on_delete=models.CASCADE, related_name="routine_exercises", db_index=True
    )
    exercise = models.ForeignKey(
        "exercises.Exercise",
        on_delete=models.CASCADE,
        related_name="routine_exercises",
        db_index=True,
    )
    order = models.IntegerField(default=0)
    sets = models.IntegerField(blank=True, null=True)
    repetitions = models.CharField(max_length=50, blank=True, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    tempo = models.CharField(max_length=50, blank=True, null=True)
    rest_seconds = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "routine_exercises"
        verbose_name = "Routine Exercise"
        verbose_name_plural = "Routine Exercises"
        indexes: ClassVar[list] = [
            models.Index(fields=["block"]),
            models.Index(fields=["exercise"]),
            models.Index(fields=["order"]),
        ]
        ordering: ClassVar[list[str]] = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.exercise.name} - {self.block}"

    def save(self, *args, **kwargs) -> None:
        """Asigna order automáticamente si no se proporciona."""
        if not self.order and self.block_id:
            max_order = RoutineExercise.objects.filter(block=self.block).aggregate(
                max_order=models.Max("order")
            )["max_order"]
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)
