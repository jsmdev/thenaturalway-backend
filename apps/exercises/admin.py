from __future__ import annotations

from typing import ClassVar

from django.contrib import admin
from django.db.models import Case, F, IntegerField, Value, When

from apps.exercises.models import Equipment, Exercise, MovementType, MuscleGroup


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "id",
        "name",
        "display_name",
        "parent",
        "order",
        "is_active",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = ["is_active", "parent", "created_at"]
    search_fields: ClassVar[list[str]] = ["name", "display_name", "description"]
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]
    list_select_related: ClassVar[list[str]] = ["parent"]
    fieldsets: ClassVar[tuple] = (
        ("Información Básica", {"fields": ("name", "display_name", "description")}),
        ("Jerarquía", {"fields": ("parent",)}),
        ("Configuración", {"fields": ("is_active", "order")}),
        ("Metadatos", {"fields": ("id", "created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Optimiza consultas y ordena jerárquicamente: padres primero, luego subgrupos justo debajo."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("parent")
        # Anotar con ID del parent para ordenamiento (usar id propio si no tiene parent)
        queryset = queryset.annotate(
            parent_id_for_sort=Case(
                When(parent__isnull=True, then=F("id")),
                default=F("parent_id"),
                output_field=IntegerField(),
            ),
            is_parent=Case(
                When(parent__isnull=True, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
        )
        # Ordenar: primero por grupo (padre + sus hijos), luego por tipo (padre antes que hijos),
        # finalmente por order y name
        return queryset.order_by("parent_id_for_sort", "is_parent", "order", "name")


@admin.register(MovementType)
class MovementTypeAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "id",
        "name",
        "display_name",
        "order",
        "is_active",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = ["is_active", "created_at"]
    search_fields: ClassVar[list[str]] = ["name", "display_name", "description"]
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]
    ordering: ClassVar[list[str]] = ["order", "name"]
    fieldsets: ClassVar[tuple] = (
        ("Información Básica", {"fields": ("name", "display_name", "description")}),
        ("Configuración", {"fields": ("is_active", "order")}),
        ("Metadatos", {"fields": ("id", "created_at", "updated_at")}),
    )


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "id",
        "name",
        "display_name",
        "order",
        "is_active",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = ["is_active", "created_at"]
    search_fields: ClassVar[list[str]] = ["name", "display_name", "description"]
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]
    ordering: ClassVar[list[str]] = ["order", "name"]
    fieldsets: ClassVar[tuple] = (
        ("Información Básica", {"fields": ("name", "display_name", "description")}),
        ("Configuración", {"fields": ("is_active", "order")}),
        ("Metadatos", {"fields": ("id", "created_at", "updated_at")}),
    )


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
        "movement_type",
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
