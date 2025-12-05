from __future__ import annotations

from typing import ClassVar

from django.contrib import admin

from apps.routines.models import Block, Day, Routine, RoutineExercise, Week


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "name",
        "created_by",
        "duration_weeks",
        "duration_months",
        "is_active",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = ["is_active", "created_at"]
    search_fields: ClassVar[list[str]] = ["name", "description"]
    readonly_fields: ClassVar[list[str]] = ["created_at", "updated_at"]
    raw_id_fields: ClassVar[list[str]] = ["created_by"]


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = ["routine", "week_number", "created_at"]
    list_filter: ClassVar[list[str]] = ["routine", "created_at"]
    search_fields: ClassVar[list[str]] = ["routine__name", "notes"]
    readonly_fields: ClassVar[list[str]] = ["created_at", "updated_at"]
    raw_id_fields: ClassVar[list[str]] = ["routine"]


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = ["week", "day_number", "name", "created_at"]
    list_filter: ClassVar[list[str]] = ["week__routine", "created_at"]
    search_fields: ClassVar[list[str]] = ["name", "notes", "week__routine__name"]
    readonly_fields: ClassVar[list[str]] = ["created_at", "updated_at"]
    raw_id_fields: ClassVar[list[str]] = ["week"]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = ["day", "name", "order", "created_at"]
    list_filter: ClassVar[list[str]] = ["day__week__routine", "created_at"]
    search_fields: ClassVar[list[str]] = ["name", "notes"]
    readonly_fields: ClassVar[list[str]] = ["created_at", "updated_at"]
    raw_id_fields: ClassVar[list[str]] = ["day"]


@admin.register(RoutineExercise)
class RoutineExerciseAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "block",
        "exercise",
        "order",
        "sets",
        "repetitions",
        "weight",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = ["block__day__week__routine", "created_at"]
    search_fields: ClassVar[list[str]] = ["exercise__name", "notes"]
    readonly_fields: ClassVar[list[str]] = ["created_at", "updated_at"]
    raw_id_fields: ClassVar[list[str]] = ["block", "exercise"]
