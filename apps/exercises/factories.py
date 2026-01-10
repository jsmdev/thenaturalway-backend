from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from apps.exercises.models import Difficulty, Equipment, Exercise, MovementType, MuscleGroup
from apps.users.factories import UserFactory


class MuscleGroupFactory(DjangoModelFactory):
    """Factory para crear grupos musculares de prueba."""

    class Meta:
        model = MuscleGroup
        django_get_or_create = ("name",)

    name = factory.Iterator(
        ["chest", "back", "shoulders", "arms", "legs", "core", "full_body", "other"]
    )
    display_name = factory.LazyAttribute(lambda obj: obj.name.capitalize())
    parent = None  # Por defecto sin padre (categoría principal)
    is_active = True
    order = factory.Sequence(lambda n: n)


class MovementTypeFactory(DjangoModelFactory):
    """Factory para crear tipos de movimiento de prueba."""

    class Meta:
        model = MovementType
        django_get_or_create = ("name",)

    name = factory.Iterator(["push", "pull", "squat", "hinge", "carry", "other"])
    display_name = factory.LazyAttribute(lambda obj: obj.name.capitalize())
    is_active = True
    order = factory.Sequence(lambda n: n)


class EquipmentFactory(DjangoModelFactory):
    """Factory para crear equipamiento de prueba."""

    class Meta:
        model = Equipment
        django_get_or_create = ("name",)

    name = factory.Iterator(
        ["barbell", "dumbbell", "bodyweight", "machine", "cable", "kettlebell", "other"]
    )
    display_name = factory.LazyAttribute(lambda obj: obj.name.capitalize())
    is_active = True
    order = factory.Sequence(lambda n: n)


class DifficultyFactory(DjangoModelFactory):
    """Factory para crear niveles de dificultad de prueba."""

    class Meta:
        model = Difficulty
        django_get_or_create = ("name",)

    name = factory.Iterator(["beginner", "intermediate", "advanced"])
    display_name = factory.LazyAttribute(
        lambda obj: {
            "beginner": "Principiante",
            "intermediate": "Intermedio",
            "advanced": "Avanzado",
        }.get(obj.name, "Principiante")
    )
    is_active = True
    order = factory.Sequence(lambda n: n)


class ExerciseFactory(DjangoModelFactory):
    """Factory para crear ejercicios de prueba."""

    class Meta:
        model = Exercise

    name = factory.Sequence(lambda n: f"Exercise {n}")
    description = factory.Faker("text", max_nb_chars=200)
    movement_type = factory.SubFactory(MovementTypeFactory)
    primary_muscle_group = factory.SubFactory(MuscleGroupFactory)
    equipment = factory.SubFactory(EquipmentFactory)
    difficulty = factory.SubFactory(DifficultyFactory)
    is_active = True
    created_by = factory.SubFactory(UserFactory)
