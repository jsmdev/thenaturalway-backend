from __future__ import annotations

from typing import ClassVar

from django.contrib import admin

from apps.sessions.models import Session, SessionExercise


class SessionExerciseInline(admin.TabularInline):
    """Inline admin para ejercicios de sesión."""

    model = SessionExercise
    extra = 0
    fields: ClassVar[list[str]] = [
        "exercise",
        "order",
        "sets_completed",
        "repetitions",
        "weight",
        "rpe",
        "rest_seconds",
        "notes",
    ]
    readonly_fields: ClassVar[list[str]] = ["created_at", "updated_at"]


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "id",
        "user",
        "routine",
        "date",
        "duration_minutes",
        "rpe",
        "energy_level",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = ["user", "routine", "date", "energy_level", "created_at"]
    search_fields: ClassVar[list[str]] = ["user__username", "routine__name", "notes"]
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]
    inlines: ClassVar[list] = [SessionExerciseInline]
    fieldsets: ClassVar[tuple] = (
        ("Información Básica", {"fields": ("user", "routine", "date")}),
        ("Tiempo", {"fields": ("start_time", "end_time", "duration_minutes")}),
        ("Métricas", {"fields": ("rpe", "energy_level", "sleep_hours")}),
        ("Notas", {"fields": ("notes",)}),
        ("Metadatos", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(SessionExercise)
class SessionExerciseAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "id",
        "session",
        "exercise",
        "order",
        "sets_completed",
        "weight",
        "rpe",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = ["session__user", "session__date", "exercise", "created_at"]
    search_fields: ClassVar[list[str]] = ["session__user__username", "exercise__name", "notes"]
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]
    fieldsets: ClassVar[tuple] = (
        ("Relaciones", {"fields": ("session", "exercise", "order")}),
        (
            "Ejecución",
            {"fields": ("sets_completed", "repetitions", "weight", "rpe", "rest_seconds")},
        ),
        ("Notas", {"fields": ("notes",)}),
        ("Metadatos", {"fields": ("created_at", "updated_at")}),
    )
