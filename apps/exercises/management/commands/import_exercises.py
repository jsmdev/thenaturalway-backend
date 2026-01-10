from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.exercises.models import Difficulty, Equipment, Exercise, MovementType, MuscleGroup


class Command(BaseCommand):
    """Comando para importar ejercicios desde un archivo JSON."""

    help = "Importa ejercicios desde un archivo JSON"

    def add_arguments(self, parser):
        """Añade argumentos al comando."""
        parser.add_argument(
            "json_file",
            type=str,
            help="Ruta al archivo JSON con los ejercicios a importar",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula la importación sin guardar en la base de datos",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Actualiza ejercicios existentes si el nombre coincide",
        )

    def handle(self, *args: tuple, **options: dict) -> None:
        """Ejecuta el comando de importación."""
        json_file = Path(options["json_file"])
        dry_run = options["dry_run"]
        update = options["update"]

        if not json_file.exists():
            self.stdout.write(self.style.ERROR(f"✗ Archivo no encontrado: {json_file}"))
            return

        self.stdout.write(self.style.WARNING(f"Leyendo archivo: {json_file}"))

        try:
            with open(json_file, encoding="utf-8") as f:
                exercises_data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"✗ Error al leer JSON: {e}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error al abrir archivo: {e}"))
            return

        if not isinstance(exercises_data, list):
            self.stdout.write(self.style.ERROR("✗ El JSON debe ser un array de objetos"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"✓ Encontrados {len(exercises_data)} ejercicios para importar")
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("⚠️  DRY RUN - No se guardará nada en la base de datos")
            )

        created_count = 0
        updated_count = 0
        error_count = 0
        errors: list[tuple[str, str]] = []

        try:
            with transaction.atomic():
                for idx, exercise_data in enumerate(exercises_data, 1):
                    try:
                        result = self._import_exercise(
                            exercise_data, update=update, dry_run=dry_run
                        )
                        if result["status"] == "created":
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"  [{idx}] ✓ Creado: {exercise_data['name']}")
                            )
                        elif result["status"] == "updated":
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"  [{idx}] ✓ Actualizado: {exercise_data['name']}"
                                )
                            )
                        elif result["status"] == "skipped":
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  [{idx}] ⊘ Omitido (ya existe): {exercise_data['name']}"
                                )
                            )
                    except Exception as e:
                        error_count += 1
                        exercise_name = exercise_data.get("name", "desconocido")
                        errors.append((exercise_name, str(e)))
                        self.stdout.write(
                            self.style.ERROR(f"  [{idx}] ✗ Error en '{exercise_name}': {e}")
                        )

                if dry_run:
                    # Rollback en dry-run
                    raise transaction.TransactionManagementError("Dry run - rollback")

        except transaction.TransactionManagementError:
            # Rollback esperado en dry-run
            pass

        # Resumen
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("RESUMEN DE IMPORTACIÓN"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Total procesados: {len(exercises_data)}")
        self.stdout.write(self.style.SUCCESS(f"  ✓ Creados: {created_count}"))
        if update:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Actualizados: {updated_count}"))
        self.stdout.write(self.style.ERROR(f"  ✗ Errores: {error_count}"))

        if errors:
            self.stdout.write("\n" + self.style.ERROR("ERRORES DETALLADOS:"))
            for exercise_name, error_msg in errors:
                self.stdout.write(f"  - {exercise_name}: {error_msg}")

        if dry_run:
            self.stdout.write(
                "\n"
                + self.style.WARNING(
                    "⚠️  Esta fue una simulación. Ejecuta sin --dry-run para importar."
                )
            )

    def _import_exercise(
        self, exercise_data: dict, update: bool = False, dry_run: bool = False
    ) -> dict:
        """Importa un ejercicio individual desde los datos del JSON."""
        name = exercise_data.get("name")
        if not name:
            raise ValueError("El campo 'name' es requerido")

        # Resolver movimiento por nombre
        movement_type = None
        if exercise_data.get("movement_type"):
            try:
                movement_type = MovementType.objects.get(name=exercise_data["movement_type"])
            except MovementType.DoesNotExist as e:
                raise ValueError(
                    f"Tipo de movimiento '{exercise_data['movement_type']}' no encontrado. "
                    f"Tipos disponibles: {', '.join(MovementType.objects.values_list('name', flat=True))}"
                ) from e

        # Resolver grupo muscular principal por nombre
        primary_muscle_group = None
        if exercise_data.get("primary_muscle_group"):
            try:
                primary_muscle_group = MuscleGroup.objects.get(
                    name=exercise_data["primary_muscle_group"]
                )
            except MuscleGroup.DoesNotExist as e:
                raise ValueError(
                    f"Grupo muscular '{exercise_data['primary_muscle_group']}' no encontrado. "
                    f"Grupos disponibles: {', '.join(MuscleGroup.objects.values_list('name', flat=True))}"
                ) from e

        # Validar grupos musculares secundarios
        secondary_muscle_groups = exercise_data.get("secondary_muscle_groups", [])
        if secondary_muscle_groups:
            if not isinstance(secondary_muscle_groups, list):
                raise ValueError("secondary_muscle_groups debe ser un array")
            # Validar que existan
            existing_groups = set(MuscleGroup.objects.values_list("name", flat=True))
            invalid_groups = set(secondary_muscle_groups) - existing_groups
            if invalid_groups:
                raise ValueError(
                    f"Grupos musculares secundarios no encontrados: {', '.join(invalid_groups)}"
                )

        # Resolver equipamiento por nombre
        equipment = None
        if exercise_data.get("equipment"):
            try:
                equipment = Equipment.objects.get(name=exercise_data["equipment"])
            except Equipment.DoesNotExist as e:
                raise ValueError(
                    f"Equipamiento '{exercise_data['equipment']}' no encontrado. "
                    f"Equipamiento disponible: {', '.join(Equipment.objects.values_list('name', flat=True))}"
                ) from e

        # Validar dificultad
        difficulty_name = exercise_data.get("difficulty")
        difficulty = None
        if difficulty_name:
            try:
                difficulty = Difficulty.objects.get(name=difficulty_name, is_active=True)
            except Difficulty.DoesNotExist:
                valid_difficulties = list(
                    Difficulty.objects.filter(is_active=True).values_list("name", flat=True)
                )
                raise ValueError(
                    f"Dificultad inválida: '{difficulty_name}'. "
                    f"Valores válidos: {', '.join(valid_difficulties)}"
                ) from None

        # Verificar si ya existe
        existing_exercise = Exercise.objects.filter(name=name).first()

        if existing_exercise and not update:
            return {"status": "skipped"}

        # Preparar datos para crear/actualizar
        exercise_fields = {
            "name": name,
            "description": exercise_data.get("description"),
            "movement_type": movement_type,
            "primary_muscle_group": primary_muscle_group,
            "secondary_muscle_groups": secondary_muscle_groups,
            "equipment": equipment,
            "difficulty": difficulty,
            "instructions": exercise_data.get("instructions"),
            "image_url": exercise_data.get("image_url"),
            "video_url": exercise_data.get("video_url"),
            "is_active": exercise_data.get("is_active", True),
        }

        if dry_run:
            # En dry-run, solo validamos sin guardar
            return {"status": "created" if not existing_exercise else "updated"}

        if existing_exercise and update:
            # Actualizar ejercicio existente
            for field, value in exercise_fields.items():
                setattr(existing_exercise, field, value)
            existing_exercise.save()
            return {"status": "updated"}

        # Crear nuevo ejercicio
        Exercise.objects.create(**exercise_fields)
        return {"status": "created"}
