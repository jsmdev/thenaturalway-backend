from __future__ import annotations

from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuración del admin para el modelo User."""

    list_display: ClassVar[list[str]] = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = [
        "is_active",
        "is_staff",
        "is_superuser",
        "gender",
        "created_at",
    ]
    search_fields: ClassVar[list[str]] = ["username", "email", "first_name", "last_name"]
    ordering: ClassVar[list[str]] = ["-created_at"]
    filter_horizontal: ClassVar[tuple[str, str]] = ("groups", "user_permissions")

    fieldsets: ClassVar[tuple] = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "date_of_birth", "gender")},
        ),
        ("Physical info", {"fields": ("height", "weight")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets: ClassVar[tuple] = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    readonly_fields: ClassVar[list[str]] = ["created_at", "updated_at", "last_login"]
