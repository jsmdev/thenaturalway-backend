from django.contrib import admin
from apps.exercises.models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'primary_muscle_group', 'equipment', 'difficulty', 'is_active', 'created_by', 'created_at']
    list_filter = ['primary_muscle_group', 'equipment', 'difficulty', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Clasificación', {
            'fields': ('movement_type', 'primary_muscle_group', 'secondary_muscle_groups', 'equipment', 'difficulty')
        }),
        ('Contenido', {
            'fields': ('instructions', 'image_url', 'video_url')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

