from __future__ import annotations

from typing import ClassVar

from django.contrib import admin

from apps.exercises.models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "id",
        "name",
        "primary_muscle_group",
        "equipment",
        "difficulty",
        "is_active",
        "created_by",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = [
        "primary_muscle_group",
        "equipment",
        "difficulty",
        "is_active",
        "created_at",
    ]
    search_fields: ClassVar[list[str]] = ["name", "description"]
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]
    fieldsets: ClassVar[tuple] = (
        ("Información Básica", {"fields": ("name", "description", "is_active")}),
        (
            "Clasificación",
            {
                "fields": (
                    "movement_type",
                    "primary_muscle_group",
                    "secondary_muscle_groups",
                    "equipment",
                    "difficulty",
                )
            },
        ),
        ("Contenido", {"fields": ("instructions", "image_url", "video_url")}),
        ("Metadatos", {"fields": ("created_by", "created_at", "updated_at")}),
    )
