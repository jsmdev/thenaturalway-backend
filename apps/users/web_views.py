from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator

from apps.users.forms import UserRegisterForm, UserLoginForm, UserProfileUpdateForm
from apps.users.services import (
    register_user_service,
    authenticate_user_service,
    get_user_profile_service,
    update_user_profile_service,
)
from apps.users.repositories import get_user_by_username_repository

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


class UserRegisterView(View):
    """Vista para registro de usuarios."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra el formulario de registro."""
        if request.user.is_authenticated:
            return redirect("users:profile")

        form = UserRegisterForm()
        return render(request, "users/register.html", {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        """Procesa el formulario de registro."""
        if request.user.is_authenticated:
            return redirect("users:profile")

        form = UserRegisterForm(request.POST)

        if not form.is_valid():
            return render(request, "users/register.html", {"form": form})

        try:
            # Registrar usuario usando el servicio
            user = register_user_service(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data.get("first_name") or None,
                last_name=form.cleaned_data.get("last_name") or None,
                date_of_birth=form.cleaned_data.get("date_of_birth").isoformat()
                if form.cleaned_data.get("date_of_birth")
                else None,
                gender=form.cleaned_data.get("gender") or None,
                height=float(form.cleaned_data["height"]) if form.cleaned_data.get("height") else None,
                weight=float(form.cleaned_data["weight"]) if form.cleaned_data.get("weight") else None,
            )

            # Autenticar al usuario automáticamente
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}! Tu cuenta ha sido creada exitosamente.")
            return redirect("users:profile")

        except Exception as error:
            messages.error(request, f"Error al registrar usuario: {str(error)}")
            return render(request, "users/register.html", {"form": form})


class UserLoginView(View):
    """Vista para inicio de sesión."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra el formulario de inicio de sesión."""
        if request.user.is_authenticated:
            return redirect("users:profile")

        form = UserLoginForm()
        return render(request, "users/login.html", {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        """Procesa el formulario de inicio de sesión."""
        if request.user.is_authenticated:
            return redirect("users:profile")

        form = UserLoginForm(request.POST)

        if not form.is_valid():
            return render(request, "users/login.html", {"form": form})

        try:
            # Autenticar usuario usando el servicio
            user = authenticate_user_service(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            if not user:
                messages.error(request, "Credenciales inválidas. Por favor, intenta de nuevo.")
                return render(request, "users/login.html", {"form": form})

            # Crear sesión Django
            login(request, user)
            messages.success(request, f"¡Bienvenido de nuevo, {user.username}!")
            return redirect("users:profile")

        except Exception as error:
            messages.error(request, f"Error al iniciar sesión: {str(error)}")
            return render(request, "users/login.html", {"form": form})


class UserLogoutView(View):
    """Vista para cerrar sesión."""

    @method_decorator(login_required)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Cierra la sesión del usuario."""
        from django.contrib.auth import logout

        logout(request)
        messages.success(request, "Has cerrado sesión correctamente.")
        return redirect("users:login")

    @method_decorator(login_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Permite cerrar sesión también con GET."""
        return self.post(request)


class UserProfileView(View):
    """Vista para ver y actualizar el perfil del usuario."""

    @method_decorator(login_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra el perfil del usuario."""
        profile_data = get_user_profile_service(user=request.user)
        form = UserProfileUpdateForm(
            initial={
                "first_name": profile_data.get("firstName"),
                "last_name": profile_data.get("lastName"),
                "date_of_birth": profile_data.get("dateOfBirth"),
                "gender": profile_data.get("gender"),
                "height": profile_data.get("height"),
                "weight": profile_data.get("weight"),
            }
        )

        context = {
            "profile": profile_data,
            "form": form,
        }

        return render(request, "users/profile.html", context)

    @method_decorator(login_required)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Actualiza el perfil del usuario."""
        form = UserProfileUpdateForm(request.POST)

        if not form.is_valid():
            profile_data = get_user_profile_service(user=request.user)
            return render(request, "users/profile.html", {"profile": profile_data, "form": form})

        try:
            # Actualizar usuario usando el servicio
            updated_user = update_user_profile_service(
                user=request.user,
                first_name=form.cleaned_data.get("first_name") or None,
                last_name=form.cleaned_data.get("last_name") or None,
                date_of_birth=form.cleaned_data.get("date_of_birth").isoformat()
                if form.cleaned_data.get("date_of_birth")
                else None,
                gender=form.cleaned_data.get("gender") or None,
                height=float(form.cleaned_data["height"]) if form.cleaned_data.get("height") else None,
                weight=float(form.cleaned_data["weight"]) if form.cleaned_data.get("weight") else None,
            )

            messages.success(request, "Tu perfil ha sido actualizado correctamente.")
            return redirect("users:profile")

        except Exception as error:
            messages.error(request, f"Error al actualizar perfil: {str(error)}")
            profile_data = get_user_profile_service(user=request.user)
            return render(request, "users/profile.html", {"profile": profile_data, "form": form})


