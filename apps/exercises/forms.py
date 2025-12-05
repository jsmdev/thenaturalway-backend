from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from apps.exercises.models import Exercise


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
    movement_type = forms.ChoiceField(
        choices=[("", "---------"), *Exercise.MOVEMENT_TYPE_CHOICES],
        required=False,
        label="Tipo de movimiento",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    primary_muscle_group = forms.ChoiceField(
        choices=[("", "---------"), *Exercise.PRIMARY_MUSCLE_GROUP_CHOICES],
        required=False,
        label="Grupo muscular principal",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    equipment = forms.ChoiceField(
        choices=[("", "---------"), *Exercise.EQUIPMENT_CHOICES],
        required=False,
        label="Equipamiento",
        widget=forms.Select(attrs={"class": "form-control"}),
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

    def clean_movement_type(self) -> str | None:
        """Valida que el tipo de movimiento sea válido si se proporciona."""
        movement_type = self.cleaned_data.get("movement_type")
        if movement_type == "":
            return None
        return movement_type

    def clean_primary_muscle_group(self) -> str | None:
        """Valida que el grupo muscular principal sea válido si se proporciona."""
        primary_muscle_group = self.cleaned_data.get("primary_muscle_group")
        if primary_muscle_group == "":
            return None
        return primary_muscle_group

    def clean_equipment(self) -> str | None:
        """Valida que el equipamiento sea válido si se proporciona."""
        equipment = self.cleaned_data.get("equipment")
        if equipment == "":
            return None
        return equipment

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
