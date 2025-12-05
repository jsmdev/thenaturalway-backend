from django.contrib import admin

from apps.sessions.models import Session, SessionExercise


class SessionExerciseInline(admin.TabularInline):
    """Inline admin para ejercicios de sesión."""

    model = SessionExercise
    extra = 0
    fields = [
        "exercise",
        "order",
        "sets_completed",
        "repetitions",
        "weight",
        "rpe",
        "rest_seconds",
        "notes",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "routine",
        "date",
        "duration_minutes",
        "rpe",
        "energy_level",
        "created_at",
    ]
    list_filter = ["user", "routine", "date", "energy_level", "created_at"]
    search_fields = ["user__username", "routine__name", "notes"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [SessionExerciseInline]
    fieldsets = (
        ("Información Básica", {"fields": ("user", "routine", "date")}),
        ("Tiempo", {"fields": ("start_time", "end_time", "duration_minutes")}),
        ("Métricas", {"fields": ("rpe", "energy_level", "sleep_hours")}),
        ("Notas", {"fields": ("notes",)}),
        ("Metadatos", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(SessionExercise)
class SessionExerciseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "session",
        "exercise",
        "order",
        "sets_completed",
        "weight",
        "rpe",
        "created_at",
    ]
    list_filter = ["session__user", "session__date", "exercise", "created_at"]
    search_fields = ["session__user__username", "exercise__name", "notes"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Relaciones", {"fields": ("session", "exercise", "order")}),
        (
            "Ejecución",
            {"fields": ("sets_completed", "repetitions", "weight", "rpe", "rest_seconds")},
        ),
        ("Notas", {"fields": ("notes",)}),
        ("Metadatos", {"fields": ("created_at", "updated_at")}),
    )
