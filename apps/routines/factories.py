from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from apps.exercises.factories import ExerciseFactory
from apps.routines.models import Block, Day, Routine, RoutineExercise, Week
from apps.users.factories import UserFactory


class RoutineFactory(DjangoModelFactory):
    """Factory para crear rutinas de prueba."""

    class Meta:
        model = Routine

    name = factory.Sequence(lambda n: f"Routine {n}")
    description = factory.Faker("text", max_nb_chars=200)
    duration_weeks = factory.Faker("random_int", min=4, max=24)
    is_active = True
    created_by = factory.SubFactory(UserFactory)


class WeekFactory(DjangoModelFactory):
    """Factory para crear semanas de prueba."""

    class Meta:
        model = Week

    routine = factory.SubFactory(RoutineFactory)
    week_number = factory.Sequence(lambda n: n + 1)
    notes = factory.Faker("text", max_nb_chars=100)


class DayFactory(DjangoModelFactory):
    """Factory para crear días de prueba."""

    class Meta:
        model = Day

    week = factory.SubFactory(WeekFactory)
    day_number = factory.Sequence(lambda n: (n % 7) + 1)
    name = factory.LazyAttribute(lambda obj: f"Day {obj.day_number}")
    notes = factory.Faker("text", max_nb_chars=100)


class BlockFactory(DjangoModelFactory):
    """Factory para crear bloques de prueba."""

    class Meta:
        model = Block

    day = factory.SubFactory(DayFactory)
    name = factory.Sequence(lambda n: f"Block {n}")
    order = factory.Sequence(lambda n: n + 1)
    notes = factory.Faker("text", max_nb_chars=100)


class RoutineExerciseFactory(DjangoModelFactory):
    """Factory para crear ejercicios en rutina de prueba."""

    class Meta:
        model = RoutineExercise

    block = factory.SubFactory(BlockFactory)
    exercise = factory.SubFactory(ExerciseFactory)
    order = factory.Sequence(lambda n: n + 1)
    sets = factory.Faker("random_int", min=1, max=5)
    repetitions = factory.Iterator(["8-10", "10-12", "12-15", "15-20"])
    weight = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    rest_seconds = factory.Iterator([30, 60, 90, 120])
