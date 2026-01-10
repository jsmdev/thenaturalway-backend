# Generated manually for converting difficulty from CharField to ForeignKey

import django.db.models.deletion
from django.db import migrations, models


def populate_initial_difficulties(apps, schema_editor):
    """Pobla los niveles de dificultad iniciales en castellano."""
    Difficulty = apps.get_model("exercises", "Difficulty")

    difficulties = [
        ("beginner", "Principiante", 1),
        ("intermediate", "Intermedio", 2),
        ("advanced", "Avanzado", 3),
    ]
    for name, display_name, order in difficulties:
        Difficulty.objects.get_or_create(
            name=name, defaults={"display_name": display_name, "order": order, "is_active": True}
        )


def reverse_populate_initial_difficulties(apps, schema_editor):
    """Revierte la migración eliminando las dificultades iniciales."""
    Difficulty = apps.get_model("exercises", "Difficulty")

    Difficulty.objects.filter(name__in=["beginner", "intermediate", "advanced"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("exercises", "0004_musclegroup_parent_and_more"),
    ]

    operations = [
        # Create Difficulty model
        migrations.CreateModel(
            name="Difficulty",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=50, unique=True)),
                ("display_name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("order", models.IntegerField(db_index=True, default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Difficulty",
                "verbose_name_plural": "Difficulties",
                "db_table": "difficulties",
                "ordering": ["order", "name"],
                "indexes": [
                    models.Index(fields=["name"], name="difficulties_name_idx"),
                    models.Index(fields=["is_active"], name="difficulties_is_active_idx"),
                    models.Index(fields=["order"], name="difficulties_order_idx"),
                ],
            },
        ),
        # Populate initial difficulties
        migrations.RunPython(populate_initial_difficulties, reverse_populate_initial_difficulties),
    ]
