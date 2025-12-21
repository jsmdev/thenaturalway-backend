from __future__ import annotations

from typing import ClassVar

from django import forms
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


class SecondaryMuscleGroupsWidget(forms.SelectMultiple):
    """Widget personalizado para grupos musculares secundarios."""

    def __init__(self, attrs=None):
        super().__init__(attrs)


class ExerciseAdminForm(forms.ModelForm):
    """Formulario personalizado para Exercise en admin."""

    secondary_muscle_groups = forms.ModelMultipleChoiceField(
        queryset=MuscleGroup.objects.none(),
        required=False,
        widget=SecondaryMuscleGroupsWidget(attrs={"class": "vSelectMultiple"}),
        help_text="Selecciona uno o más grupos secundarios (opcional). Se actualizarán según el grupo principal seleccionado.",
    )

    class Meta:
        model = Exercise
        fields: ClassVar[list[str]] = [
            "name",
            "description",
            "movement_type",
            "primary_muscle_group",
            "secondary_muscle_groups",
            "equipment",
            "difficulty",
            "instructions",
            "image_url",
            "video_url",
            "is_active",
            "created_by",
        ]

    def __init__(self, *args, **kwargs) -> None:
        """Inicializa el formulario filtrando grupos principales."""
        super().__init__(*args, **kwargs)
        # Filtrar primary_muscle_group a solo grupos principales
        self.fields["primary_muscle_group"].queryset = MuscleGroup.objects.filter(
            is_active=True, parent=None
        ).order_by("order", "name")
        self.fields["primary_muscle_group"].required = True

        # Si estamos editando, cargar grupos secundarios seleccionados
        if self.instance and self.instance.pk:
            secondary_names = self.instance.secondary_muscle_groups or []
            if secondary_names:
                secondary_groups = MuscleGroup.objects.filter(
                    name__in=secondary_names, is_active=True
                )
                self.fields["secondary_muscle_groups"].queryset = secondary_groups
                self.initial["secondary_muscle_groups"] = [sg.id for sg in secondary_groups]

    def save(self, commit=True):
        """Guarda el ejercicio convirtiendo grupos secundarios a nombres."""
        instance = super().save(commit=False)
        secondary_groups = self.cleaned_data.get("secondary_muscle_groups", [])
        if secondary_groups:
            instance.secondary_muscle_groups = [sg.name for sg in secondary_groups]
        else:
            instance.secondary_muscle_groups = []
        if commit:
            instance.save()
        return instance


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    form = ExerciseAdminForm
    change_form_template = "admin/exercises/exercise/change_form.html"
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

    def render_change_form(self, request, context, *args, **kwargs):
        """Añade datos de grupos musculares al contexto para JavaScript."""
        # Cargar grupos principales con sus subgrupos
        main_groups = (
            MuscleGroup.objects.filter(is_active=True, parent=None)
            .prefetch_related("subgroups")
            .order_by("order", "name")
        )

        # Estructurar datos para JavaScript (indexado por id porque el admin usa id por defecto)
        muscle_groups_data: dict[int, dict] = {}
        for main_group in main_groups:
            muscle_groups_data[main_group.id] = {
                "name": main_group.name,
                "display_name": main_group.display_name,
                "subgroups": [
                    {
                        "id": sg.id,
                        "name": sg.name,
                        "display_name": sg.display_name,
                    }
                    for sg in main_group.subgroups.filter(is_active=True).order_by("order", "name")
                ],
            }

        # Añadir datos al contexto (json_script hace el json.dumps automáticamente)
        context["muscle_groups_data"] = muscle_groups_data

        # Obtener IDs de grupos secundarios seleccionados (si estamos editando)
        if context.get("original"):
            exercise = context["original"]
            secondary_group_names = exercise.secondary_muscle_groups or []
            if secondary_group_names:
                secondary_groups = MuscleGroup.objects.filter(
                    name__in=secondary_group_names, is_active=True
                )
                context["selected_secondary_ids"] = [sg.id for sg in secondary_groups]
            else:
                context["selected_secondary_ids"] = []
        else:
            context["selected_secondary_ids"] = []

        return super().render_change_form(request, context, *args, **kwargs)
