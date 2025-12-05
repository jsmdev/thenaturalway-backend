from django.contrib import admin

from apps.routines.models import Block, Day, Routine, RoutineExercise, Week


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_by",
        "duration_weeks",
        "duration_months",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["created_by"]


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ["routine", "week_number", "created_at"]
    list_filter = ["routine", "created_at"]
    search_fields = ["routine__name", "notes"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["routine"]


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ["week", "day_number", "name", "created_at"]
    list_filter = ["week__routine", "created_at"]
    search_fields = ["name", "notes", "week__routine__name"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["week"]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ["day", "name", "order", "created_at"]
    list_filter = ["day__week__routine", "created_at"]
    search_fields = ["name", "notes"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["day"]


@admin.register(RoutineExercise)
class RoutineExerciseAdmin(admin.ModelAdmin):
    list_display = ["block", "exercise", "order", "sets", "repetitions", "weight", "created_at"]
    list_filter = ["block__day__week__routine", "created_at"]
    search_fields = ["exercise__name", "notes"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["block", "exercise"]
