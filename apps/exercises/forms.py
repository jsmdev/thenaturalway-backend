from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from apps.exercises.models import Equipment, Exercise, MovementType, MuscleGroup


class ExerciseForm(forms.Form):
    """Formulario base para crear y actualizar ejercicios."""

    name = forms.CharField(
        max_length=255,
        required=True,
        label="Nombre",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nombre del ejercicio"}
        ),
    )
    description = forms.CharField(
        required=False,
        label="Descripción",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 4, "placeholder": "Descripción del ejercicio"}
        ),
    )
    movement_type = forms.ModelChoiceField(
        queryset=MovementType.objects.filter(is_active=True).order_by("order", "name"),
        required=False,
        empty_label="---------",
        label="Tipo de movimiento",
        widget=forms.Select(attrs={"class": "form-control"}),
        to_field_name="name",
    )
    primary_muscle_group = forms.ModelChoiceField(
        queryset=MuscleGroup.objects.filter(is_active=True, parent=None).order_by("order", "name"),
        required=True,
        empty_label="---------",
        label="Grupo muscular principal",
        widget=forms.Select(attrs={"class": "form-control"}),
        to_field_name="name",
    )
    secondary_muscle_groups = forms.ModelMultipleChoiceField(
        queryset=MuscleGroup.objects.none(),
        required=False,
        label="Grupos musculares secundarios",
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        help_text="Selecciona uno o más grupos secundarios (opcional)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Actualizar queryset de grupos secundarios si hay datos
        if self.data:
            primary_group_name = self.data.get("primary_muscle_group")
            if primary_group_name:
                try:
                    primary_group = MuscleGroup.objects.get(name=primary_group_name, is_active=True)
                    self.fields["secondary_muscle_groups"].queryset = MuscleGroup.objects.filter(
                        is_active=True, parent=primary_group
                    ).order_by("order", "name")
                except MuscleGroup.DoesNotExist:
                    pass
        elif self.initial.get("secondary_muscle_groups"):
            # Para formularios de edición con valores iniciales
            self.fields["secondary_muscle_groups"].queryset = MuscleGroup.objects.filter(
                is_active=True, parent__isnull=False
            ).order_by("order", "name")

    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(is_active=True).order_by("order", "name"),
        required=False,
        empty_label="---------",
        label="Equipamiento",
        widget=forms.Select(attrs={"class": "form-control"}),
        to_field_name="name",
    )
    difficulty = forms.ChoiceField(
        choices=[("", "---------"), *Exercise.DIFFICULTY_CHOICES],
        required=False,
        label="Dificultad",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    instructions = forms.CharField(
        required=False,
        label="Instrucciones",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 6, "placeholder": "Instrucciones de ejecución"}
        ),
    )
    image_url = forms.URLField(
        required=False,
        label="URL de imagen",
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "https://ejemplo.com/imagen.jpg"}
        ),
    )
    video_url = forms.URLField(
        required=False,
        label="URL de video",
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "https://ejemplo.com/video.mp4"}
        ),
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Activo",
        widget=forms.CheckboxInput(attrs={"class": "form-control"}),
    )

    def clean_name(self) -> str:
        """Valida que el nombre no esté vacío."""
        name = self.cleaned_data.get("name")
        if name and not name.strip():
            raise ValidationError("El nombre no puede estar vacío.")
        return name.strip() if name else name

    def clean_movement_type(self) -> MovementType | None:
        """Valida que el tipo de movimiento sea válido si se proporciona."""
        return self.cleaned_data.get("movement_type")

    def clean_primary_muscle_group(self) -> MuscleGroup | None:
        """Valida que el grupo muscular principal sea válido y sea un grupo principal."""
        primary_muscle_group = self.cleaned_data.get("primary_muscle_group")
        if primary_muscle_group and primary_muscle_group.parent is not None:
            raise ValidationError(
                "El grupo muscular principal debe ser un grupo principal (sin padre)."
            )
        return primary_muscle_group

    def clean_secondary_muscle_groups(self) -> list[MuscleGroup]:
        """Valida que los grupos secundarios sean válidos y sean hijos del principal."""
        secondary_muscle_groups = self.cleaned_data.get("secondary_muscle_groups") or []
        primary_muscle_group = self.cleaned_data.get("primary_muscle_group")

        if not secondary_muscle_groups:
            return []

        if not primary_muscle_group:
            raise ValidationError(
                "No se pueden seleccionar grupos secundarios sin un grupo principal."
            )

        # Validar que todos los secundarios sean hijos directos del principal
        invalid_groups = [
            sg for sg in secondary_muscle_groups if sg.parent_id != primary_muscle_group.id
        ]

        if invalid_groups:
            group_names = ", ".join([g.display_name for g in invalid_groups])
            raise ValidationError(
                f"Los siguientes grupos no son subgrupos de '{primary_muscle_group.display_name}': {group_names}"
            )

        return list(secondary_muscle_groups)

    def clean_equipment(self) -> Equipment | None:
        """Valida que el equipamiento sea válido si se proporciona."""
        return self.cleaned_data.get("equipment")

    def clean_difficulty(self) -> str | None:
        """Valida que la dificultad sea válida si se proporciona."""
        difficulty = self.cleaned_data.get("difficulty")
        if difficulty == "":
            return None
        return difficulty


class ExerciseCreateForm(ExerciseForm):
    """Formulario para crear un nuevo ejercicio."""

    pass


class ExerciseUpdateForm(ExerciseForm):
    """Formulario para actualizar un ejercicio existente."""

    name = forms.CharField(
        max_length=255,
        required=False,
        label="Nombre",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nombre del ejercicio"}
        ),
    )
    primary_muscle_group = forms.ModelChoiceField(
        queryset=MuscleGroup.objects.filter(is_active=True, parent=None).order_by("order", "name"),
        required=False,
        empty_label="---------",
        label="Grupo muscular principal",
        widget=forms.Select(attrs={"class": "form-control"}),
        to_field_name="name",
    )
