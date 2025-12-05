from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Exercise(models.Model):
    """Modelo de ejercicio según el dominio."""

    MOVEMENT_TYPE_CHOICES = [
        ("push", "Push"),
        ("pull", "Pull"),
        ("squat", "Squat"),
        ("hinge", "Hinge"),
        ("carry", "Carry"),
        ("other", "Other"),
    ]

    PRIMARY_MUSCLE_GROUP_CHOICES = [
        ("chest", "Chest"),
        ("back", "Back"),
        ("shoulders", "Shoulders"),
        ("arms", "Arms"),
        ("legs", "Legs"),
        ("core", "Core"),
        ("full_body", "Full Body"),
        ("other", "Other"),
    ]

    EQUIPMENT_CHOICES = [
        ("barbell", "Barbell"),
        ("dumbbell", "Dumbbell"),
        ("cable", "Cable"),
        ("machine", "Machine"),
        ("bodyweight", "Bodyweight"),
        ("kettlebell", "Kettlebell"),
        ("other", "Other"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    movement_type = models.CharField(
        max_length=20, choices=MOVEMENT_TYPE_CHOICES, blank=True, null=True
    )
    primary_muscle_group = models.CharField(
        max_length=20, choices=PRIMARY_MUSCLE_GROUP_CHOICES, blank=True, null=True, db_index=True
    )
    secondary_muscle_groups = models.JSONField(default=list, blank=True)
    equipment = models.CharField(
        max_length=20, choices=EQUIPMENT_CHOICES, blank=True, null=True, db_index=True
    )
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, blank=True, null=True, db_index=True
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
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["primary_muscle_group"]),
            models.Index(fields=["equipment"]),
            models.Index(fields=["difficulty"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name
