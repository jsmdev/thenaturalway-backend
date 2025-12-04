from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError

from apps.users.models import User
from apps.users.repositories import get_user_by_username_repository, get_user_by_email_repository

if TYPE_CHECKING:
    pass


class UserRegisterForm(forms.Form):
    """Formulario para registro de usuarios."""

    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}),
    )
    password = forms.CharField(
        required=True,
        min_length=8,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mínimo 8 caracteres"}),
        help_text="La contraseña debe tener al menos 8 caracteres.",
    )
    password_confirm = forms.CharField(
        required=True,
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Repite la contraseña"}),
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Nombre",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre (opcional)"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Apellidos",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellidos (opcional)"}),
    )
    date_of_birth = forms.DateField(
        required=False,
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        required=False,
        label="Género",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    height = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        label="Altura (cm)",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Altura en centímetros (opcional)"}),
    )
    weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        label="Peso (kg)",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Peso en kilogramos (opcional)"}),
    )

    def clean_username(self) -> str:
        """Valida que el username sea único."""
        username = self.cleaned_data.get("username")
        if username and get_user_by_username_repository(username=username):
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self) -> str:
        """Valida que el email sea único."""
        email = self.cleaned_data.get("email")
        if email and get_user_by_email_repository(email=email):
            raise ValidationError("Este email ya está en uso.")
        return email

    def clean_password(self) -> str:
        """Valida que la contraseña tenga al menos 8 caracteres."""
        password = self.cleaned_data.get("password")
        if password and len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

    def clean(self) -> dict:
        """Valida que las contraseñas coincidan."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError({"password_confirm": "Las contraseñas no coinciden."})

        return cleaned_data


class UserLoginForm(forms.Form):
    """Formulario para inicio de sesión."""

    username = forms.CharField(
        required=True,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
    )
    password = forms.CharField(
        required=True,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
    )


class UserProfileUpdateForm(forms.Form):
    """Formulario para actualizar el perfil del usuario."""

    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Nombre",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Apellidos",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    date_of_birth = forms.DateField(
        required=False,
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        required=False,
        label="Género",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    height = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        label="Altura (cm)",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        label="Peso (kg)",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )



