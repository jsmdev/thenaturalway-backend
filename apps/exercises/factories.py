from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from apps.exercises.models import Exercise
from apps.users.factories import UserFactory


class ExerciseFactory(DjangoModelFactory):
    """Factory para crear ejercicios de prueba."""

    class Meta:
        model = Exercise

    name = factory.Sequence(lambda n: f"Exercise {n}")
    description = factory.Faker("text", max_nb_chars=200)
    movement_type = factory.Iterator(["push", "pull", "legs", "core", "cardio"])
    primary_muscle_group = factory.Iterator(
        ["chest", "back", "shoulders", "arms", "legs", "core", "full_body"]
    )
    equipment = factory.Iterator(["barbell", "dumbbell", "bodyweight", "machine", "cable", "other"])
    difficulty = factory.Iterator(["beginner", "intermediate", "advanced"])
    is_active = True
    created_by = factory.SubFactory(UserFactory)
