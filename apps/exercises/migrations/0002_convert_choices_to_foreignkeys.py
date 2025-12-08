# Generated manually for converting choices to ForeignKeys

import django.db.models.deletion
from django.db import migrations, models


def populate_initial_options(apps, schema_editor):
    """Pobla las opciones iniciales desde los valores hardcodeados."""
    MuscleGroup = apps.get_model("exercises", "MuscleGroup")
    MovementType = apps.get_model("exercises", "MovementType")
    Equipment = apps.get_model("exercises", "Equipment")

    # Poblar MuscleGroup
    muscle_groups = [
        ("chest", "Chest", 1),
        ("back", "Back", 2),
        ("shoulders", "Shoulders", 3),
        ("arms", "Arms", 4),
        ("legs", "Legs", 5),
        ("core", "Core", 6),
        ("full_body", "Full Body", 7),
        ("other", "Other", 8),
    ]
    for name, display_name, order in muscle_groups:
        MuscleGroup.objects.get_or_create(
            name=name, defaults={"display_name": display_name, "order": order, "is_active": True}
        )

    # Poblar MovementType
    movement_types = [
        ("push", "Push", 1),
        ("pull", "Pull", 2),
        ("squat", "Squat", 3),
        ("hinge", "Hinge", 4),
        ("carry", "Carry", 5),
        ("other", "Other", 6),
    ]
    for name, display_name, order in movement_types:
        MovementType.objects.get_or_create(
            name=name, defaults={"display_name": display_name, "order": order, "is_active": True}
        )

    # Poblar Equipment
    equipment_list = [
        ("barbell", "Barbell", 1),
        ("dumbbell", "Dumbbell", 2),
        ("cable", "Cable", 3),
        ("machine", "Machine", 4),
        ("bodyweight", "Bodyweight", 5),
        ("kettlebell", "Kettlebell", 6),
        ("other", "Other", 7),
    ]
    for name, display_name, order in equipment_list:
        Equipment.objects.get_or_create(
            name=name, defaults={"display_name": display_name, "order": order, "is_active": True}
        )


def reverse_populate_initial_options(apps, schema_editor):
    """Revierte la migración eliminando las opciones iniciales."""
    MuscleGroup = apps.get_model("exercises", "MuscleGroup")
    MovementType = apps.get_model("exercises", "MovementType")
    Equipment = apps.get_model("exercises", "Equipment")

    # Eliminar MuscleGroups
    MuscleGroup.objects.filter(
        name__in=["chest", "back", "shoulders", "arms", "legs", "core", "full_body", "other"]
    ).delete()

    # Eliminar MovementTypes
    MovementType.objects.filter(name__in=["push", "pull", "squat", "hinge", "carry", "other"]).delete()

    # Eliminar Equipment
    Equipment.objects.filter(
        name__in=["barbell", "dumbbell", "cable", "machine", "bodyweight", "kettlebell", "other"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("exercises", "0001_initial"),
    ]

    operations = [
        # Create MuscleGroup model
        migrations.CreateModel(
            name="MuscleGroup",
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
                "verbose_name": "Muscle Group",
                "verbose_name_plural": "Muscle Groups",
                "db_table": "muscle_groups",
                "ordering": ["order", "name"],
                "indexes": [
                    models.Index(fields=["name"], name="muscle_groups_name_idx"),
                    models.Index(fields=["is_active"], name="muscle_groups_is_active_idx"),
                    models.Index(fields=["order"], name="muscle_groups_order_idx"),
                ],
            },
        ),
        # Create MovementType model
        migrations.CreateModel(
            name="MovementType",
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
                "verbose_name": "Movement Type",
                "verbose_name_plural": "Movement Types",
                "db_table": "movement_types",
                "ordering": ["order", "name"],
                "indexes": [
                    models.Index(fields=["name"], name="movement_types_name_idx"),
                    models.Index(fields=["is_active"], name="movement_types_is_active_idx"),
                    models.Index(fields=["order"], name="movement_types_order_idx"),
                ],
            },
        ),
        # Create Equipment model
        migrations.CreateModel(
            name="Equipment",
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
                "verbose_name": "Equipment",
                "verbose_name_plural": "Equipment",
                "db_table": "equipment",
                "ordering": ["order", "name"],
                "indexes": [
                    models.Index(fields=["name"], name="equipment_name_idx"),
                    models.Index(fields=["is_active"], name="equipment_is_active_idx"),
                    models.Index(fields=["order"], name="equipment_order_idx"),
                ],
            },
        ),
        # Populate initial data
        migrations.RunPython(populate_initial_options, reverse_populate_initial_options),
        # Modify Exercise model: change movement_type to ForeignKey
        migrations.AlterField(
            model_name="exercise",
            name="movement_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="exercises",
                to="exercises.movementtype",
            ),
        ),
        # Modify Exercise model: change primary_muscle_group to ForeignKey
        migrations.AlterField(
            model_name="exercise",
            name="primary_muscle_group",
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="exercises",
                to="exercises.musclegroup",
            ),
        ),
        # Modify Exercise model: change equipment to ForeignKey
        migrations.AlterField(
            model_name="exercise",
            name="equipment",
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="exercises",
                to="exercises.equipment",
            ),
        ),
    ]
