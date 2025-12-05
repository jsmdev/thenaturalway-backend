from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from apps.exercises.models import Exercise
from apps.routines.models import Routine
from apps.sessions.models import Session


class SessionCreateForm(forms.Form):
    """Formulario para crear una nueva sesión."""

    date = forms.DateField(
        required=True,
        label="Fecha",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    routine = forms.ModelChoiceField(
        queryset=Routine.objects.none(),  # Se establecerá en la vista
        required=False,
        label="Rutina",
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Sin rutina",
    )
    start_time = forms.DateTimeField(
        required=False,
        label="Hora de inicio",
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
    )
    end_time = forms.DateTimeField(
        required=False,
        label="Hora de finalización",
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
    )
    notes = forms.CharField(
        required=False,
        label="Notas",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Notas generales de la sesión",
            }
        ),
    )
    rpe = forms.IntegerField(
        required=False,
        label="RPE (Rate of Perceived Exertion)",
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "1-10", "min": "1", "max": "10"}
        ),
        help_text="Escala de 1 a 10",
    )
    energy_level = forms.ChoiceField(
        choices=[("", "---------")] + Session.ENERGY_LEVEL_CHOICES,
        required=False,
        label="Nivel de energía",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    sleep_hours = forms.DecimalField(
        required=False,
        label="Horas de sueño",
        max_digits=4,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Ej: 7.5", "step": "0.1"}
        ),
        help_text="Horas de sueño la noche anterior",
    )

    def __init__(self, *args, user=None, **kwargs):
        """Inicializa el formulario con el usuario para filtrar rutinas."""
        super().__init__(*args, **kwargs)
        if user:
            self.fields["routine"].queryset = Routine.objects.filter(
                created_by=user, is_active=True
            )

    def clean_rpe(self) -> int | None:
        """Valida que RPE esté entre 1 y 10."""
        rpe = self.cleaned_data.get("rpe")
        if rpe is not None and (rpe < 1 or rpe > 10):
            raise ValidationError("RPE debe estar entre 1 y 10")
        return rpe

    def clean_energy_level(self) -> str | None:
        """Valida que el nivel de energía sea válido si se proporciona."""
        energy_level = self.cleaned_data.get("energy_level")
        if energy_level == "":
            return None
        return energy_level

    def clean(self) -> dict:
        """Valida que end_time sea posterior a start_time si ambos están presentes."""
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError(
                    {"end_time": "La hora de finalización debe ser posterior a la hora de inicio"}
                )

        return cleaned_data


class SessionUpdateForm(SessionCreateForm):
    """Formulario para actualizar una sesión existente."""

    date = forms.DateField(
        required=False,
        label="Fecha",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )


class SessionExerciseForm(forms.Form):
    """Formulario para crear y actualizar ejercicios en una sesión."""

    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.filter(is_active=True),
        required=True,
        label="Ejercicio",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    order = forms.IntegerField(
        required=False,
        label="Orden",
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Se asignará automáticamente si se deja vacío",
            }
        ),
        help_text="Orden del ejercicio en la sesión",
    )
    sets_completed = forms.IntegerField(
        required=False,
        label="Series completadas",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    )
    repetitions = forms.CharField(
        required=False,
        label="Repeticiones",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 8-10, 10, 12"}),
        help_text="Puede ser un rango (8-10) o valores específicos",
    )
    weight = forms.DecimalField(
        required=False,
        label="Peso (kg)",
        max_digits=8,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Ej: 80.5", "step": "0.1"}
        ),
    )
    rpe = forms.IntegerField(
        required=False,
        label="RPE",
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "1-10", "min": "1", "max": "10"}
        ),
        help_text="Rate of Perceived Exertion (1-10)",
    )
    rest_seconds = forms.IntegerField(
        required=False,
        label="Descanso (segundos)",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    )
    notes = forms.CharField(
        required=False,
        label="Notas",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Notas específicas sobre este ejercicio",
            }
        ),
    )

    def clean_rpe(self) -> int | None:
        """Valida que RPE esté entre 1 y 10."""
        rpe = self.cleaned_data.get("rpe")
        if rpe is not None and (rpe < 1 or rpe > 10):
            raise ValidationError("RPE debe estar entre 1 y 10")
        return rpe
