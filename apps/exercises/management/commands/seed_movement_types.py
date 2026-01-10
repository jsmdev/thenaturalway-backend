from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.exercises.models import Equipment, MovementType


class Command(BaseCommand):
    """Comando para poblar la base de datos con tipos de movimiento y equipamiento."""

    help = "Pobla la base de datos con tipos de movimiento y equipamiento básicos"

    def handle(self, *args: tuple, **options: dict) -> None:
        """Ejecuta el comando para poblar tipos de movimiento y equipamiento."""
        self.stdout.write(self.style.WARNING("Creando tipos de movimiento..."))

        movement_types = [
            {"name": "push", "display_name": "Empuje", "order": 1},
            {"name": "pull", "display_name": "Tirón", "order": 2},
            {"name": "squat", "display_name": "Sentadilla", "order": 3},
            {"name": "hinge", "display_name": "Bisagra", "order": 4},
            {"name": "core", "display_name": "Core", "order": 5},
            {"name": "carry", "display_name": "Carga", "order": 6},
            {"name": "other", "display_name": "Otro", "order": 7},
        ]

        created_movement_types = 0
        for mt_data in movement_types:
            movement_type, created = MovementType.objects.get_or_create(
                name=mt_data["name"],
                defaults={
                    "display_name": mt_data["display_name"],
                    "order": mt_data["order"],
                    "is_active": True,
                },
            )
            if created:
                created_movement_types += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Creado: {movement_type.display_name} ({movement_type.name})"
                    )
                )
            else:
                self.stdout.write(
                    f"  ⊘ Ya existe: {movement_type.display_name} ({movement_type.name})"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Tipos de movimiento procesados: {created_movement_types} nuevos, "
                f"{len(movement_types) - created_movement_types} existentes"
            )
        )

        self.stdout.write(self.style.WARNING("\nCreando equipamiento..."))

        equipment_list = [
            {"name": "barbell", "display_name": "Barra", "order": 1},
            {"name": "dumbbell", "display_name": "Mancuerna", "order": 2},
            {"name": "bodyweight", "display_name": "Peso Corporal", "order": 3},
            {"name": "machine", "display_name": "Máquina", "order": 4},
            {"name": "cable", "display_name": "Cable/Polea", "order": 5},
            {"name": "kettlebell", "display_name": "Kettlebell", "order": 6},
            {"name": "other", "display_name": "Otro", "order": 7},
        ]

        created_equipment = 0
        for eq_data in equipment_list:
            equipment, created = Equipment.objects.get_or_create(
                name=eq_data["name"],
                defaults={
                    "display_name": eq_data["display_name"],
                    "order": eq_data["order"],
                    "is_active": True,
                },
            )
            if created:
                created_equipment += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Creado: {equipment.display_name} ({equipment.name})")
                )
            else:
                self.stdout.write(f"  ⊘ Ya existe: {equipment.display_name} ({equipment.name})")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Equipamiento procesado: {created_equipment} nuevos, "
                f"{len(equipment_list) - created_equipment} existentes"
            )
        )

        total_movement_types = MovementType.objects.count()
        total_equipment = Equipment.objects.count()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("RESUMEN"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Total tipos de movimiento: {total_movement_types}")
        self.stdout.write(f"  Total equipamiento: {total_equipment}")
