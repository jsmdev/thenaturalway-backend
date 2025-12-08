from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.exercises.models import MuscleGroup


class Command(BaseCommand):
    """Comando para poblar la base de datos con grupos musculares jerárquicos."""

    help = "Pobla la base de datos con grupos musculares en estructura jerárquica"

    def handle(self, *args: tuple, **options: dict) -> None:
        """Ejecuta el comando para poblar grupos musculares."""
        self.stdout.write(self.style.WARNING("Eliminando grupos musculares existentes..."))
        MuscleGroup.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Grupos musculares eliminados."))

        self.stdout.write(self.style.WARNING("Creando grupos musculares..."))

        # Grupos principales sin subgrupos
        MuscleGroup.objects.create(
            name="chest",
            display_name="Pecho",
            description="Grupo muscular del pecho",
            order=1,
        )

        # Back (Espalda) con subgrupos
        back = MuscleGroup.objects.create(
            name="back",
            display_name="Espalda",
            description="Grupo muscular de la espalda",
            order=2,
        )
        MuscleGroup.objects.create(
            name="lats",
            display_name="Dorsales",
            description="Músculos dorsales",
            parent=back,
            order=1,
        )
        MuscleGroup.objects.create(
            name="traps",
            display_name="Trapecios",
            description="Músculos trapecios",
            parent=back,
            order=2,
        )
        MuscleGroup.objects.create(
            name="lower_back",
            display_name="Lumbar",
            description="Músculos lumbares",
            parent=back,
            order=3,
        )

        # Arms (Brazos) con subgrupos
        arms = MuscleGroup.objects.create(
            name="arms",
            display_name="Brazos",
            description="Grupo muscular de los brazos",
            order=3,
        )
        MuscleGroup.objects.create(
            name="biceps",
            display_name="Bíceps",
            description="Músculos bíceps",
            parent=arms,
            order=1,
        )
        MuscleGroup.objects.create(
            name="triceps",
            display_name="Tríceps",
            description="Músculos tríceps",
            parent=arms,
            order=2,
        )
        MuscleGroup.objects.create(
            name="forearms",
            display_name="Antebrazos",
            description="Músculos del antebrazo",
            parent=arms,
            order=3,
        )

        # Shoulders (Hombros) con subgrupos
        shoulders = MuscleGroup.objects.create(
            name="shoulders",
            display_name="Hombros",
            description="Grupo muscular de los hombros",
            order=4,
        )
        MuscleGroup.objects.create(
            name="front_delt",
            display_name="Deltoides Anterior",
            description="Deltoides frontal",
            parent=shoulders,
            order=1,
        )
        MuscleGroup.objects.create(
            name="side_delt",
            display_name="Deltoides Lateral",
            description="Deltoides lateral",
            parent=shoulders,
            order=2,
        )
        MuscleGroup.objects.create(
            name="rear_delt",
            display_name="Deltoides Posterior",
            description="Deltoides posterior",
            parent=shoulders,
            order=3,
        )

        # Legs (Piernas) con subgrupos
        legs = MuscleGroup.objects.create(
            name="legs",
            display_name="Piernas",
            description="Grupo muscular de las piernas",
            order=5,
        )
        MuscleGroup.objects.create(
            name="quadriceps",
            display_name="Cuádriceps",
            description="Músculos cuádriceps",
            parent=legs,
            order=1,
        )
        MuscleGroup.objects.create(
            name="hamstrings",
            display_name="Femoral",
            description="Músculos isquiotibiales (femorales)",
            parent=legs,
            order=2,
        )
        MuscleGroup.objects.create(
            name="calves",
            display_name="Gemelos",
            description="Músculos gemelos",
            parent=legs,
            order=3,
        )
        MuscleGroup.objects.create(
            name="glutes",
            display_name="Glúteos",
            description="Músculos glúteos",
            parent=legs,
            order=4,
        )

        # Core con subgrupos
        core = MuscleGroup.objects.create(
            name="core",
            display_name="Core",
            description="Grupo muscular del core",
            order=6,
        )
        MuscleGroup.objects.create(
            name="abs",
            display_name="Abdominales",
            description="Músculos abdominales",
            parent=core,
            order=1,
        )
        MuscleGroup.objects.create(
            name="obliques",
            display_name="Oblicuos",
            description="Músculos oblicuos",
            parent=core,
            order=2,
        )

        # Grupos principales sin subgrupos
        MuscleGroup.objects.create(
            name="cardio",
            display_name="Cardio",
            description="Ejercicios cardiovasculares",
            order=7,
        )

        MuscleGroup.objects.create(
            name="full_body",
            display_name="Cuerpo Completo",
            description="Ejercicios de cuerpo completo",
            order=8,
        )

        # Resumen
        total_groups = MuscleGroup.objects.count()
        main_groups = MuscleGroup.objects.filter(parent=None).count()
        subgroups = MuscleGroup.objects.filter(parent__isnull=False).count()

        self.stdout.write(self.style.SUCCESS("\n✓ Grupos musculares creados exitosamente!"))
        self.stdout.write(self.style.SUCCESS(f"  - Total: {total_groups} grupos"))
        self.stdout.write(self.style.SUCCESS(f"  - Principales: {main_groups} grupos"))
        self.stdout.write(self.style.SUCCESS(f"  - Subgrupos: {subgroups} grupos"))
