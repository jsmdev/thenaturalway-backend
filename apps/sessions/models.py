from __future__ import annotations

from typing import ClassVar

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Session(models.Model):
    """Modelo de sesión de entrenamiento según el dominio."""

    ENERGY_LEVEL_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("very_low", "Very Low"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("very_high", "Very High"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions", db_index=True)
    routine = models.ForeignKey(
        "routines.Routine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
        db_index=True,
    )
    date = models.DateField(db_index=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    rpe = models.IntegerField(blank=True, null=True, help_text="Rate of Perceived Exertion (1-10)")
    energy_level = models.CharField(
        max_length=20, choices=ENERGY_LEVEL_CHOICES, blank=True, null=True, db_index=True
    )
    sleep_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Horas de sueño la noche anterior",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_sessions"
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        indexes: ClassVar[list] = [
            models.Index(fields=["user"]),
            models.Index(fields=["routine"]),
            models.Index(fields=["date"]),
            models.Index(fields=["energy_level"]),
        ]
        ordering: ClassVar[list[str]] = ["-date", "-created_at"]

    def __str__(self) -> str:
        routine_name = f" - {self.routine.name}" if self.routine else ""
        return f"{self.date} - {self.user.username}{routine_name}"

    def save(self, *args, **kwargs) -> None:
        """Sobrescribe save para ejecutar validación y calcular duración."""
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Valida que los datos sean consistentes."""
        errors = {}

        # Validar RPE entre 1-10
        if self.rpe is not None and (self.rpe < 1 or self.rpe > 10):
            errors["rpe"] = "RPE debe estar entre 1 y 10"

        # Validar que end_time sea posterior a start_time
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            errors["end_time"] = "La hora de finalización debe ser posterior a la hora de inicio"

        # Calcular duración automáticamente si se proporcionan start_time y end_time
        if self.start_time and self.end_time and not self.duration_minutes:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)

        if errors:
            raise ValidationError(errors)


class SessionExercise(models.Model):
    """Modelo de ejercicio realizado en una sesión según el dominio."""

    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="session_exercises", db_index=True
    )
    exercise = models.ForeignKey(
        "exercises.Exercise",
        on_delete=models.CASCADE,
        related_name="session_exercises",
        db_index=True,
    )
    order = models.IntegerField(default=0)
    sets_completed = models.IntegerField(blank=True, null=True)
    repetitions = models.CharField(max_length=50, blank=True, null=True)
    weight = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True, help_text="Peso en kilogramos"
    )
    rpe = models.IntegerField(blank=True, null=True, help_text="Rate of Perceived Exertion (1-10)")
    rest_seconds = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "session_exercises"
        verbose_name = "Session Exercise"
        verbose_name_plural = "Session Exercises"
        indexes: ClassVar[list] = [
            models.Index(fields=["session"]),
            models.Index(fields=["exercise"]),
            models.Index(fields=["order"]),
        ]
        ordering: ClassVar[list[str]] = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.exercise.name} - {self.session}"

    def save(self, *args, **kwargs) -> None:
        """Asigna order automáticamente si no se proporciona."""
        if not self.order and self.session_id:
            max_order = SessionExercise.objects.filter(session=self.session).aggregate(
                max_order=models.Max("order")
            )["max_order"]
            self.order = (max_order or 0) + 1

        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Valida que los datos sean consistentes."""
        errors = {}

        # Validar RPE entre 1-10
        if self.rpe is not None and (self.rpe < 1 or self.rpe > 10):
            errors["rpe"] = "RPE debe estar entre 1 y 10"

        if errors:
            raise ValidationError(errors)
