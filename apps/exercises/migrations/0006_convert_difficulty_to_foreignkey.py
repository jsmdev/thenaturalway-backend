# Generated manually for converting difficulty field from CharField to ForeignKey

import django.db.models.deletion
from django.db import migrations, models


def migrate_difficulty_data(apps, schema_editor):
    """Migra los valores de difficulty de string a ForeignKey."""
    Exercise = apps.get_model("exercises", "Exercise")
    Difficulty = apps.get_model("exercises", "Difficulty")

    # Mapeo de valores antiguos a nombres de Difficulty
    difficulty_map = {
        "beginner": "beginner",
        "intermediate": "intermediate",
        "advanced": "advanced",
    }

    # Migrar cada ejercicio
    for exercise in Exercise.objects.all():
        if exercise.difficulty:  # El campo todavía es CharField aquí
            difficulty_name = exercise.difficulty
            if difficulty_name in difficulty_map:
                try:
                    difficulty_obj = Difficulty.objects.get(name=difficulty_map[difficulty_name])
                    # Asignar al nuevo campo ForeignKey
                    exercise.difficulty_new_id = difficulty_obj.id
                    exercise.save(update_fields=["difficulty_new_id"])
                except Difficulty.DoesNotExist:
                    # Si no existe, dejamos null
                    pass


def reverse_migrate_difficulty_data(apps, schema_editor):
    """Revierte la migración convirtiendo ForeignKey a string."""
    Exercise = apps.get_model("exercises", "Exercise")
    # Nota: Esta función no se ejecutará porque el campo antiguo ya fue eliminado
    # En caso de rollback, necesitaríamos recrear el campo CharField primero
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("exercises", "0005_add_difficulty_model"),
    ]

    operations = [
        # Primero, añadir un campo temporal ForeignKey nullable
        migrations.AddField(
            model_name="exercise",
            name="difficulty_new",
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="exercises.difficulty",
            ),
        ),
        # Migrar datos del campo antiguo al nuevo
        migrations.RunPython(migrate_difficulty_data, reverse_migrate_difficulty_data),
        # Eliminar el campo antiguo CharField
        migrations.RemoveField(
            model_name="exercise",
            name="difficulty",
        ),
        # Renombrar el nuevo campo al nombre original
        migrations.RenameField(
            model_name="exercise",
            old_name="difficulty_new",
            new_name="difficulty",
        ),
        # Actualizar related_name (el RenameField no actualiza esto)
        migrations.AlterField(
            model_name="exercise",
            name="difficulty",
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="exercises",
                to="exercises.difficulty",
            ),
        ),
    ]
