from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from apps.exercises.models import Exercise


class RoutineCreateForm(forms.Form):
    """Formulario para crear una nueva rutina."""

    name = forms.CharField(
        max_length=255,
        required=True,
        label="Nombre",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nombre de la rutina"}
        ),
    )
    description = forms.CharField(
        required=False,
        label="Descripción",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 4, "placeholder": "Descripción de la rutina"}
        ),
    )
    duration_weeks = forms.IntegerField(
        required=False,
        label="Duración en semanas",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    duration_months = forms.IntegerField(
        required=False,
        label="Duración en meses",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Activa",
        widget=forms.CheckboxInput(attrs={"class": "form-control"}),
    )

    def clean_name(self) -> str:
        """Valida que el nombre no esté vacío."""
        name = self.cleaned_data.get("name")
        if name and not name.strip():
            raise ValidationError("El nombre no puede estar vacío.")
        return name.strip() if name else name


class RoutineUpdateForm(forms.Form):
    """Formulario para actualizar una rutina existente."""

    name = forms.CharField(
        max_length=255,
        required=False,
        label="Nombre",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nombre de la rutina"}
        ),
    )
    description = forms.CharField(
        required=False,
        label="Descripción",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 4, "placeholder": "Descripción de la rutina"}
        ),
    )
    duration_weeks = forms.IntegerField(
        required=False,
        label="Duración en semanas",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    duration_months = forms.IntegerField(
        required=False,
        label="Duración en meses",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    is_active = forms.BooleanField(
        required=False,
        label="Activa",
        widget=forms.CheckboxInput(attrs={"class": "form-control"}),
    )

    def clean_name(self) -> str:
        """Valida que el nombre no esté vacío si se proporciona."""
        name = self.cleaned_data.get("name")
        if name and not name.strip():
            raise ValidationError("El nombre no puede estar vacío.")
        return name.strip() if name else name


class WeekForm(forms.Form):
    """Formulario para crear/editar una semana."""

    week_number = forms.IntegerField(
        required=True,
        label="Número de semana",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    notes = forms.CharField(
        required=False,
        label="Notas",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "placeholder": "Notas para esta semana"}
        ),
    )


class DayForm(forms.Form):
    """Formulario para crear/editar un día."""

    day_number = forms.IntegerField(
        required=True,
        label="Número de día",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    name = forms.CharField(
        max_length=255,
        required=False,
        label="Nombre del día",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ej: Día 1, Push Day"}
        ),
    )
    notes = forms.CharField(
        required=False,
        label="Notas",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "placeholder": "Notas para este día"}
        ),
    )


class BlockForm(forms.Form):
    """Formulario para crear/editar un bloque."""

    name = forms.CharField(
        max_length=255,
        required=True,
        label="Nombre del bloque",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ej: Pecho + Tríceps"}
        ),
    )
    order = forms.IntegerField(
        required=False,
        label="Orden",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    notes = forms.CharField(
        required=False,
        label="Notas",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "placeholder": "Notas para este bloque"}
        ),
    )

    def clean_name(self) -> str:
        """Valida que el nombre no esté vacío."""
        name = self.cleaned_data.get("name")
        if name and not name.strip():
            raise ValidationError("El nombre no puede estar vacío.")
        return name.strip() if name else name


class RoutineExerciseForm(forms.Form):
    """Formulario para crear/editar un ejercicio en rutina."""

    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.filter(is_active=True).order_by("name"),
        required=True,
        label="Ejercicio",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    order = forms.IntegerField(
        required=False,
        label="Orden",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    sets = forms.IntegerField(
        required=False,
        label="Series",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    repetitions = forms.CharField(
        max_length=50,
        required=False,
        label="Repeticiones",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 8-12"}),
    )
    weight = forms.DecimalField(
        required=False,
        label="Peso (kg)",
        max_digits=8,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    weight_percentage = forms.DecimalField(
        required=False,
        label="Porcentaje del 1RM (%)",
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    tempo = forms.CharField(
        max_length=50,
        required=False,
        label="Tempo",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 2-0-1-0"}),
    )
    rest_seconds = forms.IntegerField(
        required=False,
        label="Descanso (segundos)",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    notes = forms.CharField(
        required=False,
        label="Notas",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "placeholder": "Notas para este ejercicio"}
        ),
    )
